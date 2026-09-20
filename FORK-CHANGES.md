# What this fork changes, and how to stay in sync with upstream

Everything in this fork sits on top of the **unmodified source of an official Soul of Waifu release**.
This file lists every change, so an upstream update can be merged without losing them - and so a lost
patch is noticed immediately.

## Branch model

| Branch | Contents |
|---|---|
| `main` | upstream's GitHub branch, untouched |
| `release` | the **unmodified** source of the official release archive (`Soul-of-Waifu-vX.Y.Z.rar`), no binaries, no models, no Windows Python runtime |
| `linux` | `release` + the changes listed below (default branch) |

Upstream publishes its releases before the code reaches GitHub - `Soul-of-Waifu-v2.5.1.rar` differed from
GitHub `main` in ~60 files - so `release` is the reference, not `main`.

`git diff release..linux` is therefore always the complete, current set of our changes.

## Updating to a new upstream release

```bash
# 1. unpack the new release archive somewhere, then put its source on the release branch
git switch release
#    copy the archive's source files over the tracked ones - skip app/data/, binaries, models;
#    keep the line endings of the archive (upstream mixes CRLF and LF)
git add -A && git commit -m "Import source code of the official vX.Y.Z release"

# 2. merge it into the port
git switch linux
git merge release           # conflicts land only in the files listed below
./tools/fork_report.sh      # verifies that every change is still in place
sed -i 's/^SOW_VERSION=.*/SOW_VERSION="X.Y.Z"/' installer.sh
```

For commits that only exist on upstream's GitHub branch:

```bash
git fetch upstream && git switch linux && git merge upstream/main
```

### When a merge conflicts

Conflicts can only appear in the files under "Changed upstream files" below. Rule of thumb:

- **Keep upstream's version of the surrounding code** and re-apply our change on top - our patches are small
  and self-contained, upstream's changes are usually larger.
- Every patch is marked in the code by the search pattern in the table (`tools/fork_report.sh` checks them).
- Afterwards: `./tools/fork_report.sh` - it reports each missing patch by name.

## New files (no merge conflicts possible)

| File | Purpose |
|---|---|
| `installer.sh`, `start.sh` | Linux replacements for `installer.bat` / `start.bat` |
| `app/utils/platform_compat.py` | Linux equivalents of the Windows-only calls (`os.startfile`, `winreg`, `ctypes.windll`) |
| `tools/patch_venv.py` | venv fixes: fairseq on Python 3.11, pyworld's `pkg_resources` warning, qwen_tts' flash-attn banner |
| `tools/fetch_llama_backend.py` | downloads the llama.cpp Linux build for a backend |
| `tools/fetch_live2d_models.py` | downloads and installs matching Live2D Cubism models into `assets/emotions/live2d/` |
| `tools/build_llama_cuda.sh` | builds `llama-server` with CUDA and installs it into the backend folder - llama.cpp ships no Linux CUDA build |
| `tools/fork_report.sh` | diff against `release` + check that every patch below is present |
| `tools/import_character_cards.py` | imports `chara_card_v2` cards with their avatars, Live2D models, user personas, lorebooks and Soul Stage scenes into the configuration in bulk - no UI clicking |
| `app/translations/de.yaml` | German translation of the app. Besides every `en.yaml` key it also fills 26 gaps upstream left: keys the code asks for that exist in no language file, so all languages fall back to the English string in the code (import dialog, backup restore, scene tooltips, local server errors, …). Four keys stay untranslated on purpose - their defaults are f-strings carrying a path, chat name or error, and a YAML value would drop that detail. |
| `presets/sakura-succubus-3/` | a German preset set: seven character cards (`chara_card_v2`) with AI-generated avatars, matching Live2D models and the prompts they were made from, six Soul Stage scenes and three lorebooks - import them with the tool above |
| `README-LINUX.md`, `README_DE.md`, `FORK-CHANGES.md` | documentation |

## Changed upstream files

"Pattern" is what `tools/fork_report.sh` greps for, and what to look for after a merge.

### Linux port

| File | Change | Pattern |
|---|---|---|
| `main.py` | reports the desktop file name, so task bars show the app icon | `setDesktopFileName` |
| `main.py`, `app/utils/ai_clients/local_server_manager.py` | the llama-server outlived the app and kept the model in VRAM - it is stopped when the window closes, and on SIGTERM/SIGINT, which Qt otherwise ignores | `def shutdown_sync` |
| `app/gui/interface_signals.py` | opens folders via `platform_compat.open_path` instead of `os.startfile` | `from app.utils.platform_compat import open_path` |
| `app/gui/interface_signals.py` | asset paths use `/` instead of `\\` (Windows keeps working) | no `assets\\` left in the file |
| `app/gui/interface_signals.py` | audio device list: only the sound-server PCMs on Linux (raw ALSA devices reject the TTS sample rates) | `_selectable_audio_devices` |
| `app/gui/sow_system_signals.py` | idle time via `platform_compat`; `wintypes` import moved into the Windows branch | `get_idle_time_ms as _get_system_idle_time_ms` |
| `app/gui/sow_system_signals.py` | Live2D start guarded: a warning instead of a crash when OpenGL fails (from upstream PR #61) | `live2d_unavailable_title` |
| `app/gui/custom_widgets.py`, `app/gui/interface_signals.py`, `app/gui/sow_system_signals.py` | switching characters deletes the chat page while its timers keep calling the VRM view - "wrapped C/C++ object of type QWebEngineView has been deleted"; every call goes through a guard now | `def run_webview_js` |
| `app/gui/custom_widgets.py` | memory folder opens via `open_path` | `from app.utils.platform_compat import open_path` |
| `app/gui/custom_widgets.py`, `app/utils/platform_compat.py` | Models Hub: the folder button ran `explorer /select,` and failed with `[Errno 2] explorer` on Linux - `reveal_path` shows the file in Dolphin/Nautilus (D-Bus FileManager1, folder as fallback), Finder on macOS, Explorer on Windows; its tooltip and error message are translated | `def reveal_path` |
| `app/utils/soul_companion/soul_companion.py` | Linux versions of the companion tools: open apps/folders, media keys, clipboard, window title/focus, OS/CPU/GPU info | `_open_target_posix` |
| `app/utils/soul_companion/plugins/agentic_tools.py` | Bash instead of PowerShell, typing via wtype/ydotool/xdotool, Linux system folders protected, localized XDG folders | `_SHELL_LANGUAGE` |
| `app/utils/backend_updater.py` | llama.cpp: Ubuntu builds and `.tar.gz` extraction on Linux | `_match_linux_assets` |
| `app/utils/ai_clients/local_server_manager.py` | falls back to a system `llama-server`; `LD_LIBRARY_PATH` for the bundled build | `system llama-server` |
| `app/utils/ai_clients/local_server_manager.py` | picking the CUDA backend on Linux only said "executable not found" - llama.cpp ships no Linux CUDA build, so the message now names the three ways out | `error_no_linux_cuda_build` |
| `app/utils/ai_clients/local_server_manager.py` | a llama-server left over from an earlier run kept serving the old model and context size ("request exceeds the available context size") - a server of ours whose model, context, backend, KV cache type or chat template no longer matches the settings is restarted, a system one is only reported | `_server_configuration_mismatch` |
| `app/utils/ai_clients/local_server_manager.py` | a model that fails to load (too little VRAM) only produced "check the logs" - the last llama-server lines that name the cause are kept and shown with the error, and the message points at the GPU-layers setting | `def server_failure_reason` |
| `app/utils/text_to_speech.py` | kokoro / RVC / fairseq imports are optional, so the app starts without them | `_kokoro_error` |
| `app/utils/vrm_server.py` | `installer.sh` / `start.sh` added to the blocked paths | `"/installer.sh"` |
| `app/configuration/configuration.py` | normalizes backslash paths coming from a Windows config | `Default settings.json (and configs from the Windows version)` |
| `requirements.txt` | `pywin32` and `win32_setctime` marked as Windows-only | `sys_platform == "win32"` |
| `.gitignore` | runtime data and files copied from the release archive | `# --- Linux port` |

### Features on top of upstream

| File | Change | Pattern |
|---|---|---|
| `app/gui/sowInterface.py`, `main.py`, `app/gui/interface_signals.py`, `app/gui/soul_stage_page.py`, `app/gui/custom_widgets.py`, `app/gui/sow_system_signals.py`, `app/utils/ai_clients/local_server_manager.py` | German as the third program language (`case 2` / `2: "de"` everywhere the language is resolved) | `load_translation("de")`, `2: "de"` |
| `main.py` | translates the 6th options tab (upstream bug: never translated in any language) | `appearance_tab_name` |
| `app/gui/sowInterface.py`, `main.py`, `app/utils/ai_clients/prompt_engine.py` | **Reply Language** setting: tells the model which language to answer in, narration included | `_build_language_directive` |
| `app/utils/ai_clients/prompt_engine.py` | the story summary follows the reply language too - an English summary sits in every later prompt and pulls the model back to English | `_resolve_reply_language` |
| `app/utils/ai_clients/prompt_engine.py` | the prompt keeps as much room free for the answer as "max tokens" allows - upstream always reserved 500, so a longer answer ran into the context limit halfway | `_get_response_reserve` |
| `app/gui/sowInterface.py`, `main.py`, `app/gui/interface_signals.py`, `app/gui/sow_system_signals.py`, `app/utils/ai_clients/soul_stage_engine.py` | German as a chat translation target next to Russian | `{0: "ru", 1: "de"}` |
| `app/gui/interface_signals.py`, `main.py` | local LLM starts when a chat is opened, and a message waits for the server | `autostart_local_llm` |
| `app/gui/interface_signals.py` | loading a model from the Models Hub swallowed every error - the button stayed on "Unload" and nothing was shown; failures now raise a toast and the list is refreshed | `_on_launch_server_task_done` |
| `app/gui/sowInterface.py` | RP editor cards grow with longer translations instead of clipping them | `heightForWidth(card_width)` |
| `app/gui/interface_signals.py` | `update_lip_sync` tolerates a configuration without `character_list` | `character_list = config.get("character_list", {})` |
| `app/gui/interface_signals.py` | start page greeting picks from all variants the language file has (upstream drew 1-5 although every language ships 7) | `available = [i for i in range(1, 8)` |
| `app/gui/custom_widgets.py`, `app/gui/sowInterface.py` | the Context Inspector tooltip was hard-coded English in every language - now translated (13 keys), the widget takes the translations | `context_inspector_title` |
| `app/gui/soul_stage_page.py` | a scene stores its GM tone as the displayed text, so an imported scene (or a language switch) fell back to the first entry - the key and the English name are now mapped onto the current language | `def _tone_text` |
| `app/translations/en.yaml`, `ru.yaml` | keys for the additions above | `response_language_label` |

## Releases

| Tag | Contents |
|---|---|
| `vX.Y.Z-linux.N` | the `linux` branch itself - installed with `git clone -b linux` |
| `vX.Y.Z-win.N` | the changes that are **not** Linux-specific, as a ZIP to unpack over an official Windows installation |

The Windows patch is exactly `git diff --name-only release..linux` minus the Linux-only files
(`installer.sh`, `start.sh`, `tools/`, the READMEs, `.gitignore`, `requirements.txt`), plus a
`PATCH-README.md`. `app/utils/platform_compat.py` must stay in it - the patched modules import it:

```bash
git archive linux $(git diff --name-only release..linux \
    | grep -vE '^(installer\.sh|start\.sh|tools/|README|FORK-CHANGES|\.gitignore|requirements\.txt)') \
    | tar -x -C /tmp/winpatch
```

Check afterwards that the patch really reproduces the branch: unpack the ZIP over a checkout of
`release` and diff it against `linux` - only the Linux-only files above may differ.

## Checking

```bash
./tools/fork_report.sh          # summary + patch check
./tools/fork_report.sh --diff   # full diff against release
```

The check is a grep for the patterns above: it proves a patch is still present, not that it still works.
After a bigger upstream update, start the app once and try a chat with a local model.
