<p align="center">
  <img src="https://i.ibb.co/bj7fbNVC/Soul-of-Waifu-Banner-2.png" alt="Soul of Waifu Banner" border="0">
</p>
<h3 align="center">🌌 ONE SOUL - MULTIPLE DIMENSIONS 🌌</h3>

<p align="center">
  <b>Your character is no longer locked in a text chat - they live wherever you are.</b><br>
  <i>Welcome to the world where your AI characters chats, remembers, adventures in tabletop RPGs, and lives directly on your desktop with one continuous, evolving identity.</i><br>
</p>

---

<div align="center">
    <img src="https://count.getloli.com/get/@Soul-of-Waifu?theme=rule34" /><br>
</div>
<p align="center">
  <img alt="Downloads" src="https://img.shields.io/github/downloads/jofizcd/Soul-of-Waifu/total?style=for-the-badge&logo=github&label=Downloads">
  <img alt="Stars" src="https://img.shields.io/github/stars/jofizcd/Soul-of-Waifu?style=for-the-badge&logo=github">
  <img alt="Discord" src="https://img.shields.io/discord/925841922264801311?style=for-the-badge&logo=discord&label=Community&color=5865F2">
  <img alt="Release" src="https://img.shields.io/github/v/release/jofizcd/Soul-of-Waifu?style=for-the-badge&logo=github&color=6e40c9">
</p>
<p align="center">
  <img alt="Forks" src="https://img.shields.io/github/forks/jofizcd/Soul-of-Waifu?style=for-the-badge&logo=github">
  <img alt="License" src="https://img.shields.io/github/license/jofizcd/Soul-of-Waifu?style=for-the-badge">
  <img alt="Issues" src="https://img.shields.io/github/issues/jofizcd/Soul-of-Waifu?style=for-the-badge&logo=github">
</p>
<p align="center">
  📚 <a href="https://jofizcd.github.io/soul-of-waifu-site/"><b>Documentation</b></a> &nbsp;•&nbsp;
  🗨️ <a href="https://discord.com/invite/6vFtQGVfxM"><b>Discord</b></a> &nbsp;•&nbsp;
  🌐 <a href="https://jofizcd.github.io/soul-of-waifu-site/"><b>Website</b></a>
</p>
<p align="center">
  🌍 <b>English</b> &nbsp;•&nbsp; <a href="README_RU.md">Русский</a> &nbsp;•&nbsp; <a href="README_DE.md">Deutsch</a>
</p>
<p align="center">
  <a href="https://github.com/jofizcd/Soul-of-Waifu/releases/latest">
    <img src="https://img.shields.io/badge/ENTER A NEW REALITY-2EA043?style=for-the-badge&logo=windows&logoColor=white" alt="Download Latest">
  </a>
  <a href="README-LINUX.md">
    <img src="https://img.shields.io/badge/LINUX PORT-1793D1?style=for-the-badge&logo=linux&logoColor=white" alt="Linux port">
  </a>
  <a href="https://github.com/SnowwhiteOakheart/Soul-of-Waifu/releases/tag/v2.5.1-win.1">
    <img src="https://img.shields.io/badge/GERMAN PATCH-6e40c9?style=for-the-badge&logo=windows&logoColor=white" alt="German patch for Windows">
  </a>
</p>

> [!NOTE]
> This is a **fork of a fork**. [SnowwhiteOakheart/Soul-of-Waifu](https://github.com/SnowwhiteOakheart/Soul-of-Waifu) adds an unofficial **Linux port**, a complete **German
> translation** and a handful of fixes - see **[what this fork adds](#-what-this-fork-adds)**. This fork
> builds on it with an interface made for **Linux and Wayland** - see
> **[the Wayland interface](#-the-wayland-interface-this-fork)**.

---

## 🪟 The Wayland interface (this fork)

The `master` branch sits on top of the Linux port below and reworks the interface:

- **Native on Wayland:** the system window frame instead of the frameless window with its own
  _ □ × buttons, so tiling compositors (Hyprland, Sway, KDE, GNOME) handle the window like any other.
- **File dialogs through the XDG desktop portal:** the system file picker instead of Qt's own dialog.
- **Adaptive layout:** the window shrinks to 720×480 (was 1350×734); the sidebar hides below 1000 px
  (the ☰ button brings it back); long labels wrap; top bars and button rows wrap; card grids drop columns.
- **Themes:** Options -> Appearance -> Window Theme edits colors, spacing, corner radius, glass opacity,
  text size, interface scale and font. 16 built-in themes, your own as JSON files in
  `~/.config/soul-of-waifu/themes/` (import, export, live reload), the accent color can follow the system.
- **Fonts as sharp as in other apps:** hinting follows fontconfig, Inter Tight everywhere instead of a
  mix with the system font.
- The sidebar footer buttons are plain icons in the bottom-left corner.

Every change is listed in **[FORK-CHANGES.md](FORK-CHANGES.md)**.

## 🍴 What this fork adds

Everything here sits on top of the unmodified source of the official **v2.5.1** release.
**[FORK-CHANGES.md](FORK-CHANGES.md)** documents every single change and how to merge a new upstream
release; `./tools/fork_report.sh` verifies afterwards that none of them got lost.

### 🐧 The Linux port (base fork, `linux` branch)

- `installer.sh` and `start.sh` replace the `.bat` scripts: Python 3.11 through [`uv`](https://docs.astral.sh/uv/),
  PyTorch (CUDA/ROCm/CPU), every dependency, the llama.cpp Linux build, and the icons, backgrounds and
  avatar models out of upstream's release archive. It also creates a menu entry and a **desktop shortcut
  with a proper icon**.
- `app/utils/platform_compat.py` holds the Linux equivalents of the Windows-only calls: opening files and
  folders, launching apps through `.desktop` entries, localized XDG folders, clipboard, media keys, active
  window title and focus, idle time and hardware info.
- **Local LLMs:** the official llama.cpp Ubuntu builds (CPU/Vulkan/ROCm/SYCL) are downloaded and unpacked,
  and a system `llama-server` is used when no bundled build exists.
- **Audio:** the device list offers the sound-server PCMs, so TTS stops failing with "Invalid sample rate".
  **RVC:** fairseq 0.12.2 is made importable on Python 3.11, and the app also starts without it.
- Installation, the optional desktop tools and the full feature matrix: **[README-LINUX.md](README-LINUX.md)**.

### 🇩🇪 Not Linux-specific - this part runs on Windows too

- A complete **German translation** of the app (Options -> App Language).
- **Reply Language** (Options -> App Interface): tells the AI which language to answer in - narration,
  descriptions and inner thoughts included, not only dialogue. Follows the app language by default;
  "Let the model decide" restores the upstream behaviour.
- **German as a chat translation target**, next to Russian.
- **The local LLM starts itself:** opening a chat that uses "Local LLM" starts llama-server in the
  background, and sending a message waits for the server instead of failing with "Could not reach the
  local server". Nothing happens for cloud providers or without a configured local model.
- **26 strings translated that upstream never put in a language file** - the code asks for them, no
  language file has them, so *every* language silently fell back to English (import dialog, backup
  restore, scene tooltips, local server errors, …).
- **Soul Stage Tabletop RPG Evolution (Phases 1–5):**
  - **Live Player HUD & Clocks:** Real-time visibility of HP, Energy, Stress, active condition badges with duration counters, and a toggleable Campaign Clocks tracker.
  - **Procedural SFX & Speech:** Built-in procedural audio synthesizer (`numpy`/`sounddevice`) for rolling dice, critical fanfares, failure stingers, consumable sounds, and crackling campfires. Voice readout buttons (`🔊`) for every narrator, NPC, and companion bubble.
  - **Manual Dice Roller & Skills:** Dedicated dice button (`🎲`) allowing player-driven skill checks (d20, d100, 2d6, d6, d12) with character skill modifiers and DC target evaluation.
  - **Tagged Decision Options:** Decision cards with colored skill check and resource cost pills (Baldur's Gate 3 / Disco Elysium style).
  - **Interactive Consumable Inventory:** Clicking potions, bread, water, or bandages instantly restores HP/Energy, lowers stress, and cures ailments.
  - **Campfire Rest & Bond Milestones:** Short & Long Rests (`🏕️`), intimate campfire banter interludes, and companion affinity progression with bond milestone announcements (+25, +50, +75).
  - **Tactical Encounter Mode:** A live initiative bar and enemy HP pools appear the moment the GM starts a real fight, with one-click Attack/Dodge/Item/Flee quick actions.
- **Upstream bugs fixed:** the Appearance tab was never translated in any language; RP editor cards
  clipped longer translations; the start page greeting drew from 5 of the 7 variants each language file
  ships; `update_lip_sync` crashed on a configuration without `character_list`.
- Windows users get all of it as a drop-in patch: **[v2.5.1-win.1](https://github.com/SnowwhiteOakheart/Soul-of-Waifu/releases/tag/v2.5.1-win.1)** (687 KB, unpack over an
  official v2.5.1 installation).

### 🧰 Extras

- **[`tools/import_character_cards.py`](tools/import_character_cards.py)** imports `chara_card_v2` cards,
  their avatars and user personas in bulk, instead of clicking every character in by hand.
- **[`presets/sakura-succubus-3/`](presets/sakura-succubus-3/)** - seven German character cards with
  AI-generated avatars, as an example of that.

---

<p align="center">
  <img style="width:95%; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.6);" alt="Soul of Waifu v2.4.7 Interface" src="assets/readme/preview.gif">
</p>

---

## 🌟 What is Soul of Waifu?

**Soul of Waifu (SoW)** is a free, open-source desktop app where AI characters can remember, evolve, and exist across multiple dimensions of interaction simultaneously. The core idea: a character you create once exists across multiple interconnected modes at the same time - text and voice conversation, a full tabletop RPG engine, a desktop agent with real OS and tool access, and a persistent memory architecture that builds genuine continuity across all your sessions.

Create or import a character once, and seamlessly interact with them across interconnected dimensions:
1. **Interactive Text & Voice Chat** with customizable UI, Live2D/VRM avatars, and real-time voice calls.
2. **Soul Memory Architecture** featuring long-term emotional evolution, a personal diary, and self-healing memory logs.
3. **Soul Stage RPG Engine** running a full tabletop text-RPG driven by a dedicated AI Game Master, complete with dice rolls and hidden story arcs.
4. **Soul Companion** - an autonomous agent living on your screen, powered by neurohormonal simulation. Out of the box it can see your screen, control your mouse and keyboard, browse the web on its own, run code, and organize your files - no extra setup needed. Want more? Write your own Python plugins or connect any external MCP server to give it entirely new abilities. Every risky action is gated behind an on-screen approval system, so nothing runs without your say-so.

Everything runs **100% locally on your PC by default** - your chats with characters can live entirely offline, with no subscriptions and no filters. Cloud AI providers (OpenAI, Claude, Gemini, and others) are available as an optional plug-in for low-spec hardware or heavier reasoning, and browser/web tools naturally reach the internet when a task calls for it - but the core experience never requires an account or sends your data anywhere you haven't asked it to.

---

## 🆕 What's New Since Soul Trinity (v2.4.0)

Soul of Waifu has been moving fast since the original Soul Trinity (v2.4.0) release. The highlights:

- **Soul Companion is now a full autonomous OS agent.** It can move your mouse, click and type into any window, browse the web on its own through a real headless browser, run sandboxed Python/PowerShell scripts, organize your files, and chain multi-step tasks together - all gated behind a Human-in-the-Loop approval banner with a 25-second fail-safe countdown, so nothing risky ever runs without your say-so.
- **Soul Stage grew into a genuine tabletop RPG simulator.** Deterministic dice rolls and skill checks, hidden Story Arcs your party has to actually uncover, a live Campaign Board with pressure clocks, structural relationship tracking that never forgets a grudge or a bond, and Scene Folders to organize whole campaigns.
- **Tool calling isn't companion-exclusive anymore.** Web search, clipboard access, and app control now work in regular 1-on-1 text and voice chats too.
- **Discord Gateway got smarter.** Full computer vision for images/GIFs, plus per-member awareness so it never mixes up who said what in a server.
> The full, detailed changelog for every version lives on the [Releases page](https://github.com/jofizcd/Soul-of-Waifu/releases).

---

## 🚀 Key Modules & Capabilities

### 1. One Soul, Multiple Dimensions

Every character you build is a single continuous identity that steps through several connected modes - the same personality and memories follow them everywhere.

| Mode | Description |
|---|---|
| 🧠 **Soul Memory** | An independent digital brain for every character - tracking mood, relationships, and lived history far beyond basic keyword fact-searching. |
| 💬 **Text & Voice Chat** | Full-duplex conversation with Live2D & VRM avatars, a customizable state variable HUD, lorebooks, and real-time voice calls. |
| 🎲 **Soul Stage** | A full tabletop RPG under a virtual Game Master - dice rolls, generating options for your answers, WorldState tracking, inventory, and dynamic NPCs with its own memory. |
| 🖥️ **Soul Companion** | An autonomous desktop agent powered by neurohormones - reads your screen, controls your mouse/keyboard, browses the web on its own, runs code, and organizes your files, extensible with custom plugins and MCP servers. |

---

### 🧠 Soul Memory — Long-Term Cognitive Architecture

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Soul Memory System" src="https://i.ibb.co/zH4fqtmC/sc-screenshots-soul-memory.png">
</p>

Standard vector-RAG approaches search old chat logs for keyword matches. **Soul Memory** functions as an autonomous background agent that continuously rewrites four isolated cognitive files in real time:

- **Psychology Layer**: Tracks current mood, internal tension, hidden motives, and character development.
- **Relationship Profile**: Remembers user habits, preferences, shared promises, and trust progression.
- **Episodic Topic Archive**: Categorized knowledge base indexing locations, events, and key facts, matched against your queries using local semantic embeddings - with strong bilingual accuracy.
- **Personal Diary**: First-person reflective entries written by the character after meaningful conversations.

> [!TIP]
> **Cognitive Mechanics:**
> - **Emotional Decay:** Grudges and negative mood spikes naturally cool down over time if not revisited.
> - **Memory Self-Healing:** The system detects logical contradictions between new responses and past facts, automatically overwriting outdated information and logging corrections.
> - **Duplicate Detection:** Near-identical memories are automatically merged so the archive stays clean over long-term use.
> - **Crash-Safe Writes:** Memory updates save atomically, so an unexpected error mid-session can no longer cost you your character's memories.

Choose between **Full Sync** (maximum depth), **Soul Link** (balanced), **Mind Spark** (lightweight), or **Reflection Flow** (diary only) to fit your VRAM/RAM constraints.

---

### 🎲 Soul Stage — Tabletop RPG & Game Master Engine

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Soul Stage RPG Mode" src="https://i.ibb.co/Ld2VcVFS/sc-screenshots-soul-stage.png">
</p>

Soul Stage transitions your chat into a structured tabletop roleplaying campaign managed by a virtual Game Master. The GM is a separate AI layer running independently of your character: it maintains the world state, directs events, and enforces structure for group roleplay sessions.

- **WorldState Engine:** Rigorous state tracking for in-game time of day, weather, active location, and key facts.
- **Live Resource & Status HUD:** Continual real-time tracking of player HP (10/10), Energy (6/6), Stress (0/6), and active conditions (with remaining round durations and effect tooltips).
- **Deterministic & Manual Dice Rolls:** AI-triggered and player-initiated checks (d20, d100, 2d6, d6, d12) with skill modifiers, DC targets, and procedural dice sound effects.
- **Audio & TTS Atmosphere:** Dynamic procedural audio (dice rolls, critical fanfares, failure chords, campfire rest ambience) plus on-demand voice readout buttons on all dialog bubbles.
- **Campaign Board & Clocks Tracker:** Live objective tracking with "Pressure Clocks" (guard alert levels, ritual countdowns) that shift dynamically with your choices.
- **Tagged Choices:** Player decision options with colored skill check and resource cost badges (Baldur's Gate 3 / Disco Elysium style).
- **Interactive Consumable Inventory:** Direct one-click consumption of potions, food, water, and bandages with instant recovery and condition cures.
- **Campfire Rest & Bond Milestones:** Take short or long rests at the campfire (`🏕️`), trigger intimate companion conversations, and advance companion bond levels (+25, +50, +75).
- **Tactical Encounter Mode:** When the GM starts a genuine fight, a live initiative bar (party + enemies) and per-enemy HP bars appear above the input, with one-click ⚔️ Attack / 🛡️ Dodge / 🎒 Item / 🏃 Flee quick actions the GM resolves narratively.
- **Story Arcs:** Hidden plot twists and investigations stay concealed from NPCs and the party until concrete clues are uncovered during play.
- **Turn Control Bar:** Switch between Say, Do, Think, and Director input modes, pick the next speaker manually, or send Private Whispers only one party member can see.
- **Structural Relationship Tracker:** Trust levels and social roles are serialized and fed into every turn, so companions and NPCs never "forget" their dynamic with you, even dozens of turns later.
- **Interactive Party & NPCs:** Main party members sync memories via Soul Memory, while dynamic temporary NPCs spawn (with their own persistent memory) for specific encounters.
- **Scene Folders:** Organize your scenario library into campaigns, genres, or settings.
- **Atmospheric Automation:** Scene backgrounds and ambient audio loops switch automatically as the story moves to new locations.
- **Event Cards:** Encounter, discovery, consequence, camp, and story milestone cards keep campaigns unpredictable.

---

### 🖥️ Soul Companion — Autonomous Desktop Agent

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Soul Companion Desktop Overlay" src="https://i.ibb.co/ZzgN6LDw/sc-screenshots-soul-companion.jpg">
</p>

Soul Companion turns your character into an autonomous inhabitant of your Windows desktop - and, as of the latest release, a genuine computer-use agent. Existing as a transparent overlay, the companion stays with you while you work, game, or browse. Its behavior is driven by a neurohormone system (dopamine, cortisol, oxytocin, fatigue) rather than simple reactive prompting: it has moods that shift over time based on activity levels, time of day, and your interaction patterns, gets tired after long sessions, gets bored during extended inactivity, and initiates conversation on its own when something notable happens on your screen.

**Computer Use & OS Control:**

| Tool | What it does |
|---|---|
| 🖱️ **GUI Action Tool** | Moves the cursor, clicks (single/double/right-click), scrolls, dispatches keyboard shortcuts, and types text natively into any active window (Discord, Notepad, VS Code, browsers, etc.) |
| 🌐 **Browser Agent** | Autonomously navigates URLs, extracts clean article text, clicks buttons, fills out forms, and downloads files through a real headless browser (Playwright) |
| 🐍 **Code Execution** | Writes and runs sandboxed Python/PowerShell scripts on the fly for calculations, data parsing, or batch tasks, with strict timeouts |
| 📁 **File Organizer** | Inspects your desktop and folders, auto-sorts loose files into categories, and runs fast filename search |
| 🧭 **Task Planner** | Converts a complex spoken goal into a sequential, multi-step tool chain and executes it end-to-end |
| ❤️‍🩹 **System Vitals Watchdog** | Proactively warns you about low battery, GPU overheating, or finished downloads |
| 🔎 Screen Reader | Sees your screen and comments on, analyzes, or assists with what's visible |
| 📋 Clipboard Reader | Reads and processes copied text on request |
| 🔍 Web Search | Looks up information in real time |
| 🎵 Music Control | Manages audio playback |
| 🔌 Custom MCP Server | Connect any external MCP server for expanded integrations |

**Safety by design:** every potentially risky action - moving files, running code, controlling your mouse or keyboard - is intercepted by an on-screen approval banner with a 25-second fail-safe countdown. Nothing executes without your explicit confirmation, and the app automatically restores focus to your active window afterward so no keystrokes get lost.

---

### 📊 Custom State Variables & Adaptive HUD

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Custom State Variables HUD" src="https://i.ibb.co/rKVFcMY1/sc-screenshots-hud.png">
</p>

Build no-code Dating Sims, RPG stat systems, or Tamagotchi mechanics directly inside character cards without writing code. 
- **Adaptive HUD Bar:** Displays animated progress bars (`int`), YES/NO badges (`bool`), item lists (`list`), or text labels (`str`) at the top of the chat.
- **Resilient AI Interceptor:** Backend interceptor parses state updates robustly, making updates immune to LLM JSON syntax typos.
- **11 Built-In Presets:** Ready-to-use templates for Romance, RPG, Survival, Interrogation, Horror, and Visual Novels.

---

## 🌐 Ecosystem & Extended Integrations

### 📱 Local Web Client (Mobile / Tablet Access)

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Web Client Interface" src="https://i.ibb.co/G3cgzpFq/sc-screenshots-web-server.png">
</p>

Run Soul of Waifu on your main PC and connect from your phone or tablet over home Wi-Fi via `http://<your-pc-ip>:8000`. Features real-time bidirectional WebSocket syncing, custom chat backgrounds, avatar rendering, and voice input routed directly through your PC's local Faster Whisper model.

---

### 🤖 Discord Gateway

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Discord Gateway" src="https://i.ibb.co/xtRJ4y83/sc-screenshot-discord.png">
</p>

Connect your Soul of Waifu characters directly to Discord bots. Chat with your characters inside server channels or private messages, preserving their full personality, system prompt settings, and long-term memories.
- **Multi-User Server Awareness:** Distinguishes between individual server members and keeps a distinct conversation context per speaker.
- **Computer Vision:** Sees, inspects, and reacts to images and GIFs sent in direct messages or server channels.

---

### 🎨 AI Image Generation

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Image Generation in Chat" src="https://i.ibb.co/sv4DqPQ0/sc-screenshot-image-gen.png">
</p>

Generate illustrations directly within chat messages via context menu actions.
- **Local Engines:** Automatic1111 WebUI, ComfyUI API.
- **Cloud Engines:** NovelAI Diffusion, DALL-E 3, FLUX.
- Automatically builds contextual visual prompts based on the character's appearance, current pose, emotional state, and scene environment.

---

## 🛠️ Deep Tech & Fine-Tuning

<details>
<summary><b>🎙️ Voice, Speech-to-Text & Avatars</b></summary>

- **6 Text-to-Speech Engines:**
  - **Qwen3 TTS (Local):** Ultra-low latency, voice cloning from a 3-second audio sample, prompt-based voice design, 9 built-in speakers, 1.7B and 0.6B models.
  - **XTTSv2 & Kokoro 82M (Local):** High-fidelity voice synthesis and zero-shot voice cloning.
  - **Silero TTS (Local):** Fast Russian voice engine.
  - **EdgeTTS & ElevenLabs (Cloud):** High-quality cloud neural voices.
- **RVC Support:** Integrated Voice Conversion parameter tuning (pitch shift, index rate, protection).
- **Sentence-by-Sentence Streaming:** Audio playback starts on the first generated sentence, eliminating response lag.
- **Full-Duplex Calls (SoW System):** Silero VAD (Voice Activity Detection) + Faster Whisper transcription with seamless user-interruption support.
- **Avatars & 28 Emotion Classifier:** Live2D (with motion animation links), VRM 3D models, GIFs, and static images. Automatic 28-state emotional sentiment analysis with LipSync audio matching.

</details>

<details>
<summary><b>🎛️ Advanced Text Sampling (Loop Prevention)</b></summary>

- **Dynamic Temperature:** Dynamically shifts temperature based on confidence to balance creativity and logic.
- **DRY Sampler (Don't Repeat Yourself):** Prevents multi-word phrase loops without degrading grammatical quality.
- **XTC (Exclude Top Candidates):** Filters out overused AI clichés and repetitive vocabulary.
- **Min-P:** Trims low-probability tokens relative to the top candidate for coherent output.

</details>

<details>
<summary><b>📖 Updated Lorebooks Engine</b></summary>

- **Multi-Binding:** Link multiple lorebooks to a single character simultaneously.
- **Semantic Situation Matching:** Local vector search matches lore entries based on situational context rather than strict keywords.
- **Scene Tension Accumulator:** Dynamically builds story energy to trigger random events.
- **Chain Dependencies:** Create multi-stage questlines with delayed entry unlocks.
- **Injection Modes:** Choose between *Passive (Background Knowledge)* and *Active (System Directive)* injection.

</details>

<details>
<summary><b>💻 Local & Cloud LLM Backends</b></summary>

- **Reasoning Model Support:** Dedicated Thinking Token Budget setting and automatic `<think>` block parsing for reasoning models like DeepSeek.
- **Models Hub:** Integrated Hugging Face repository search, GGUF downloader with progress bar and instant cancel, and automated Llama.cpp binary updater.
- **Local Acceleration:** Llama.cpp HTTP server supporting **CUDA (NVIDIA)**, **HIP (AMD)**, **SYCL (Intel)**, and **Vulkan**.
- **Performance Options:** Flash Attention, MLock, KV-Cache quantization (`q8_0`, `q4_0`), Thinking Mode, and CPU MoE layer offloading.
- **10 Cloud Providers Supported:** OpenRouter, OpenAI, Anthropic Claude, DeepSeek, Grok (xAI), Google Gemini, Qwen, Mistral AI, Z.AI, Player2 and custom OpenAI-compatible endpoints.

</details>

---

## 📥 Installation

### Windows

No Python knowledge, Node.js, or command-line experience required.

```
1. Download the latest release archive (currently Soul-of-Waifu-v2.5.1.rar) from Releases.
2. Extract it with 7-Zip or WinRAR to a path without spaces or Cyrillic characters (e.g. C:\AI\Soul-Of-Waifu\).
3. Run installer.bat (Do NOT run as Administrator).
4. Launch via start.bat.
```

> [!WARNING]
> **Do not run `installer.bat` as Administrator!** Windows changes the working directory for Administrator processes to `C:\Windows\System32`, causing installation path errors. Use a standard double-click.

### 🐧 Linux

The installer sets up Python 3.11, PyTorch (CUDA/ROCm/CPU), llama.cpp and every dependency, and
copies the program files out of the official release archive:

```bash
git clone https://github.com/SilentAutomaton/Soul-of-Waifu.git
cd Soul-of-Waifu
./installer.sh     # then start with ./start.sh
```

See **[README-LINUX.md](README-LINUX.md)** for system packages, GPU backends and feature status.

### System Requirements

| | Minimum | Recommended |
|---|---|---|
| **OS** | Windows 10/11 (64-bit) or Linux (x86_64) | Windows 10/11 (64-bit) or Linux (x86_64) |
| **RAM** | 8 GB | 16 GB+ |
| **GPU** | Any (for Cloud APIs) | NVIDIA / AMD with 6+ GB VRAM (for local models) |
| **Storage** | 10 GB free space | Fast NVMe SSD |

---

## ⚡ Quick Start

- **Option A — Cloud AI (No GPU Required):**
  Go to **Options -> Configuration**, input your OpenRouter or OpenAI API key. Import a character card from the **Characters Gateway** or drag-and-drop a `.png` / `.json` file into the app window.
- **Option B — Local AI:**
  Navigate to **Models Hub**, search for a model (e.g. `Gemma` or `Qwen`), and download a `Q4_K_M` GGUF quantization. In **Options -> LLM Settings**, select your GPU backend (CUDA/HIP/SYCL/Vulkan), enable Flash Attention, and launch the server via Models Hub.

Once you're set up, web search, clipboard access, app control and other tools are available straight away in regular text and voice chats - no need to switch to Soul Companion mode to use them.
 
📖 Read full documentation & guides: **[jofizcd.github.io/soul-of-waifu-site/docs](https://jofizcd.github.io/soul-of-waifu-site/docs/)**
 
---
 
## 💖 Support & Community
 
Soul of Waifu is a solo-developer open-source project. All features are 100% free with no paywalls or premium tiers.
 
**Financial Support:**
- **[Boosty](https://boosty.to/jofizcd)**
- **[Donation Alerts](https://www.donationalerts.com/r/jofizcd)**
**Community & Help:**
- **Star this repository** - helps boost visibility on GitHub!
- **Join our [Discord Server](https://discord.com/invite/6vFtQGVfxM)** - share custom character cards, lorebooks, RPG scenes, and get help from the community.

---
 
## 📊 Repository Stats
 
<div align="center">
  <img src="https://star-history.dera.page/svg?repos=jofizcd/Soul-of-Waifu&type=Date" alt="Star History Chart"/>
</div>
<br>
<div align="center">
  <img src="https://repobeats.axiom.co/api/embed/6af186be156d185ec7424197ff77edf14db5eeb0.svg" alt="Repobeats Analytics">
</div>

---
 
## 👤 Developer
 
<div align="center">
  <a href="https://github.com/jofizcd">
    <img style="border-radius: 50%;" width="110" src="https://i.ibb.co/Hj3g4j2/ava.jpg" alt="Jofi Avatar">
  </a>
  <br><br>
  <b>Jofi</b>
  <br><br>
  <a href="https://www.youtube.com/@jofizcd">
    <img alt="YouTube" src="https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white">
  </a>
  <a href="https://discord.com/invite/6vFtQGVfxM">
    <img alt="Discord" src="https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white">
  </a>
  <a href="https://t.me/waytojofistar">
    <img alt="Telegram" src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white">
  </a>
  <a href="https://github.com/jofizcd">
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
</div>
<br>
<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License: GPL v3">
  </a>
</p>
