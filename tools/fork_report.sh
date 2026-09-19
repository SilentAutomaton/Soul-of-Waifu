#!/usr/bin/env bash
# Reports what this fork changes on top of the official release source, and checks that
# every change from FORK-CHANGES.md is still present - run it after merging an upstream update.
#
# Usage: ./tools/fork_report.sh [--diff]
#   --diff   also print the complete diff against the release branch

set -uo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."

BASE="${FORK_BASE_BRANCH:-release}"
GREEN=$'\e[0;32m'; YELLOW=$'\e[0;33m'; RED=$'\e[0;31m'; BOLD=$'\e[1m'; RESET=$'\e[0m'

# label | file | grep pattern (fixed string)
CHECKS=(
    "Linux helpers module|app/utils/platform_compat.py|IS_LINUX ="
    "Installer / launcher|installer.sh|install_shortcuts"
    "venv patches (fairseq, pyworld, qwen_tts)|tools/patch_venv.py|def patch_fairseq"
    "llama.cpp backend download|tools/fetch_llama_backend.py|_match_assets"
    "German translation|app/translations/de.yaml|program_language_item_de"

    "Desktop file name for task bars|main.py|setDesktopFileName"
    "Open folders without os.startfile|app/gui/interface_signals.py|from app.utils.platform_compat import open_path"
    "Audio devices: sound-server PCMs only|app/gui/interface_signals.py|_selectable_audio_devices"
    "Idle time via platform_compat|app/gui/sow_system_signals.py|get_idle_time_ms as _get_system_idle_time_ms"
    "Live2D start guarded|app/gui/sow_system_signals.py|live2d_unavailable_title"
    "Memory folder via open_path|app/gui/custom_widgets.py|from app.utils.platform_compat import open_path"
    "Companion tools on Linux|app/utils/soul_companion/soul_companion.py|_open_target_posix"
    "Agent tools on Linux (bash, XDG, typing)|app/utils/soul_companion/plugins/agentic_tools.py|_SHELL_LANGUAGE"
    "llama.cpp Linux builds|app/utils/backend_updater.py|_match_linux_assets"
    "System llama-server fallback|app/utils/ai_clients/local_server_manager.py|system llama-server"
    "Optional kokoro/RVC imports|app/utils/text_to_speech.py|_kokoro_error"
    "VRM server blocks the .sh scripts|app/utils/vrm_server.py|\"/installer.sh\""
    "Windows backslash paths normalized|app/configuration/configuration.py|Default settings.json (and configs from the Windows version)"
    "Windows-only requirements marked|requirements.txt|sys_platform == \"win32\""

    "German as program language|app/gui/interface_signals.py|self.load_translation(\"de\")"
    "German in the language selector|app/gui/sowInterface.py|[\"English\", \"Russian\", \"German\"]"
    "Appearance tab translated|main.py|appearance_tab_name"
    "Reply language directive|app/utils/ai_clients/prompt_engine.py|_build_language_directive"
    "Reply language selector|app/gui/sowInterface.py|comboBox_response_language"
    "German as translation target|app/gui/interface_signals.py|{0: \"ru\", 1: \"de\"}"
    "Translate to German in Soul Stage|app/utils/ai_clients/soul_stage_engine.py|ss_menu_translate_de"
    "Local LLM starts with the chat|app/gui/interface_signals.py|autostart_local_llm"
    "RP cards grow with the text|app/gui/sowInterface.py|heightForWidth(card_width)"
    "Lip sync tolerates missing character_list|app/gui/interface_signals.py|character_list = config.get(\"character_list\", {})"
    "All greeting variants are used|app/gui/interface_signals.py|available = [i for i in range(1, 8)"
    "Context Inspector translated|app/gui/custom_widgets.py|context_inspector_title"
    "GM tone survives the language|app/gui/soul_stage_page.py|def _tone_text"
    "Show a model in the file manager|app/utils/platform_compat.py|def reveal_path"
)

echo "${BOLD}Soul of Waifu - fork report${RESET}"
echo "Branch: $(git rev-parse --abbrev-ref HEAD)   base: $BASE   ($(git log -1 --format='%h %s' "$BASE" 2>/dev/null || echo 'branch missing'))"
echo

if ! git rev-parse --verify --quiet "$BASE" >/dev/null; then
    echo "${RED}No '$BASE' branch - cannot compare against the unmodified release source.${RESET}"
else
    echo "${BOLD}Changes against $BASE:${RESET}"
    git diff --stat "$BASE..HEAD" | tail -40
    echo
fi

echo "${BOLD}Patch check (see FORK-CHANGES.md):${RESET}"
missing=0
for entry in "${CHECKS[@]}"; do
    IFS='|' read -r label file pattern <<< "$entry"
    if [[ ! -f $file ]]; then
        printf "  ${RED}MISSING${RESET}  %-42s %s (file not found)\n" "$label" "$file"
        missing=$((missing + 1))
    elif grep -qF -- "$pattern" "$file"; then
        printf "  ${GREEN}ok${RESET}       %-42s %s\n" "$label" "$file"
    else
        printf "  ${RED}MISSING${RESET}  %-42s %s (pattern: %s)\n" "$label" "$file" "$pattern"
        missing=$((missing + 1))
    fi
done

# Windows-only leftovers that would break the Linux port again
echo
echo "${BOLD}Regression check:${RESET}"
leftovers=0

# 1) hard-coded backslash asset paths (our own normalization helper is not one)
backslash_hits=$(grep -rnE '"(assets|app)\\\\' --include='*.py' main.py app 2>/dev/null \
    | grep -v 'app/data/' | grep -vE 'platform_compat\.py|startswith|replace\(' || true)
if [[ -n $backslash_hits ]]; then
    echo "  ${YELLOW}Backslash asset paths came back:${RESET}"
    echo "$backslash_hits" | cut -c1-120 | sed 's/^/    /'
    leftovers=$((leftovers + 1))
else
    echo "  ${GREEN}ok${RESET}       no hard-coded backslash asset paths"
fi

# 2) os.startfile outside a Windows branch (an inline guard or a Windows-only function counts)
startfile_hits=$(
    for f in $(grep -rl 'os\.startfile' --include='*.py' main.py app 2>/dev/null | grep -v 'app/data/' | grep -v platform_compat.py); do
        awk -v file="$f" '
            /^[[:space:]]*def / {
                winfunc = ($0 ~ /def (_open_target|_find_shortcut_on_system|_focus_process_window|_read_win32_clipboard)\(/)
            }
            /os\.name *== *"nt"|sys\.platform *== *"win32"|is_windows/ { guard = NR }
            /os\.startfile/ {
                if (!winfunc && NR - guard > 15) printf "    %s:%d: %s\n", file, NR, substr($0, 1, 90)
            }
        ' "$f"
    done
)
if [[ -n $startfile_hits ]]; then
    echo "  ${YELLOW}os.startfile outside a Windows branch:${RESET}"
    echo "$startfile_hits"
    leftovers=$((leftovers + 1))
else
    echo "  ${GREEN}ok${RESET}       every os.startfile sits in a Windows branch"
fi

echo
if [[ $missing -eq 0 ]]; then
    echo "${GREEN}${BOLD}All ${#CHECKS[@]} changes are present.${RESET}"
else
    echo "${RED}${BOLD}$missing of ${#CHECKS[@]} changes are missing - see FORK-CHANGES.md.${RESET}"
fi

if [[ ${1:-} == "--diff" ]]; then
    echo
    echo "${BOLD}Full diff against $BASE:${RESET}"
    git diff "$BASE..HEAD"
fi

exit $(( missing > 0 ? 1 : 0 ))
