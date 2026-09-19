<p align="center">
  <img src="https://i.ibb.co/bj7fbNVC/Soul-of-Waifu-Banner-2.png" alt="Soul of Waifu Banner" border="0">
</p>
<h3 align="center">🌌 EINE SEELE – VIELE DIMENSIONEN 🌌</h3>

<p align="center">
  <b>Dein Charakter ist nicht länger in einem Textchat gefangen – er lebt dort, wo du bist.</b><br>
  <i>Willkommen in einer Welt, in der deine KI-Charaktere chatten, sich erinnern, mit dir in Tabletop-RPGs auf Abenteuer gehen und direkt auf deinem Desktop leben – mit einer einzigen, durchgehenden und sich stetig weiterentwickelnden Identität.</i><br>
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
  📚 <a href="https://jofizcd.github.io/soul-of-waifu-site/"><b>Dokumentation</b></a> &nbsp;•&nbsp;
  🗨️ <a href="https://discord.com/invite/6vFtQGVfxM"><b>Discord</b></a> &nbsp;•&nbsp;
  🌐 <a href="https://jofizcd.github.io/soul-of-waifu-site/"><b>Website</b></a>
</p>
<p align="center">
  🌍 <a href="README.md">English</a> &nbsp;•&nbsp; <a href="README_RU.md">Русский</a> &nbsp;•&nbsp; <b>Deutsch</b>
</p>
<p align="center">
  <a href="https://github.com/jofizcd/Soul-of-Waifu/releases/latest">
    <img src="https://img.shields.io/badge/ENTER A NEW REALITY-2EA043?style=for-the-badge&logo=windows&logoColor=white" alt="Neueste Version herunterladen">
  </a>
  <a href="README-LINUX.md">
    <img src="https://img.shields.io/badge/LINUX--VERSION-1793D1?style=for-the-badge&logo=linux&logoColor=white" alt="Linux-Portierung">
  </a>
  <a href="https://github.com/SnowwhiteOakheart/Soul-of-Waifu/releases/tag/v2.5.1-win.1">
    <img src="https://img.shields.io/badge/DEUTSCH--PATCH-6e40c9?style=for-the-badge&logo=windows&logoColor=white" alt="Deutsch-Patch für Windows">
  </a>
</p>

> [!NOTE]
> Dies ist ein **Fork**. Er ergänzt das Original um eine inoffizielle **Linux-Portierung**, eine
> vollständige **deutsche Übersetzung** und einige Fehlerbehebungen - siehe
> **[was dieser Fork mitbringt](#-was-dieser-fork-mitbringt)**.

---

## 🍴 Was dieser Fork mitbringt

Alles hier setzt auf dem unveränderten Quellcode der offiziellen **v2.5.1** auf.
**[FORK-CHANGES.md](FORK-CHANGES.md)** dokumentiert jede einzelne Änderung und beschreibt, wie sich eine
neue Version des Originals einpflegen lässt; `./tools/fork_report.sh` prüft anschließend, dass dabei
keine verloren gegangen ist.

### 🐧 Die Linux-Portierung (Branch `linux`, hier der Standard-Branch)

- `installer.sh` und `start.sh` ersetzen die `.bat`-Skripte: Python 3.11 über [`uv`](https://docs.astral.sh/uv/),
  PyTorch (CUDA/ROCm/CPU), sämtliche Abhängigkeiten, den llama.cpp-Build für Linux sowie Icons,
  Hintergründe und Avatar-Modelle aus dem offiziellen Release-Archiv. Dazu legt der Installer einen
  Menüeintrag und eine **Desktop-Verknüpfung mit passendem Icon** an.
- `app/utils/platform_compat.py` enthält die Linux-Entsprechungen der Windows-Aufrufe: Dateien und Ordner
  öffnen, Programme über `.desktop`-Einträge starten, lokalisierte XDG-Ordner (`~/Schreibtisch`,
  `~/Bilder`), Zwischenablage, Medientasten, Titel und Fokus des aktiven Fensters, Leerlaufzeit und
  Hardware-Infos.
- **Lokale LLMs:** Die offiziellen llama.cpp-Builds für Ubuntu (CPU/Vulkan/ROCm/SYCL) werden geladen und
  entpackt; ist kein mitgelieferter Build vorhanden, nutzt die App einen `llama-server` aus dem `PATH`.
- **Audio:** Die Geräteliste bietet die Geräte des Soundservers an, damit die Sprachausgabe nicht mehr an
  "Invalid sample rate" scheitert. **RVC:** fairseq 0.12.2 ist unter Python 3.11 importierbar gemacht, und
  die App startet auch ohne.
- Installation, die optionalen Desktop-Werkzeuge und die vollständige Funktionsübersicht:
  **[README-LINUX.md](README-LINUX.md)**.

### 🇩🇪 Nicht Linux-spezifisch - das läuft auch unter Windows

- Eine vollständige **deutsche Übersetzung** der App (Optionen -> App-Sprache).
- **Antwortsprache** (Optionen -> Benutzeroberfläche): legt fest, in welcher Sprache die KI antwortet -
  Erzähltext, Beschreibungen und Gedanken eingeschlossen, nicht nur der Dialog. Folgt standardmäßig der
  Sprache der Oberfläche; „Modell entscheiden lassen“ stellt das ursprüngliche Verhalten wieder her.
- **Deutsch als Ziel der Chat-Übersetzung**, zusätzlich zu Russisch.
- **Das lokale LLM startet von selbst:** Wird ein Chat mit „Lokales LLM“ geöffnet, startet llama-server im
  Hintergrund, und das Absenden einer Nachricht wartet auf den Server, statt mit „Could not reach the
  local server“ abzubrechen. Bei Cloud-Anbietern oder ohne konfiguriertes lokales Modell passiert nichts.
- **26 Texte übersetzt, die im Original in keiner Sprachdatei stehen** - der Code fragt sie ab, keine
  Sprachdatei kennt sie, also fiel *jede* Sprache stillschweigend auf Englisch zurück (Import-Dialog,
  Backup-Wiederherstellung, Szenen-Tooltips, Fehler des lokalen Servers, …).
- **Fehler des Originals behoben:** Der Reiter „Appearance“ wurde in keiner Sprache übersetzt; Karten im
  RP-Editor schnitten längere Übersetzungen ab; die Begrüßung auf der Startseite nutzte 5 der 7 Varianten,
  die jede Sprachdatei mitbringt; `update_lip_sync` stürzte ohne `character_list` ab.
- Für Windows gibt es das alles als Patch zum Drüberkopieren: **[v2.5.1-win.1](https://github.com/SnowwhiteOakheart/Soul-of-Waifu/releases/tag/v2.5.1-win.1)** (687 KB, wird über
  eine offizielle v2.5.1-Installation entpackt).

### 🧰 Extras

- **[`tools/import_character_cards.py`](tools/import_character_cards.py)** importiert `chara_card_v2`-Karten,
  ihre Avatare und Benutzer-Personas im Bündel, statt jede Figur einzeln anzuklicken.
- **[`presets/sakura-succubus-3/`](presets/sakura-succubus-3/)** - sieben deutsche Charakterkarten mit
  KI-generierten Avataren als Beispiel dafür.

---

<p align="center">
  <img style="width:95%; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.6);" alt="Oberfläche von Soul of Waifu v2.4.7" src="assets/readme/preview.gif">
</p>

---

## 🌟 Was ist Soul of Waifu?

**Soul of Waifu (SoW)** ist eine kostenlose Open-Source-Desktop-App, in der KI-Charaktere sich erinnern, weiterentwickeln und gleichzeitig in mehreren Dimensionen der Interaktion existieren können. Die Grundidee: Ein einmal erstellter Charakter lebt zugleich in mehreren miteinander verbundenen Modi – Text- und Sprachunterhaltung, eine vollwertige Tabletop-RPG-Engine, ein Desktop-Agent mit echtem Zugriff auf Betriebssystem und Werkzeuge sowie eine dauerhafte Gedächtnisarchitektur, die über alle deine Sitzungen hinweg echte Kontinuität schafft.

Erstelle oder importiere einen Charakter einmal und interagiere nahtlos über verbundene Dimensionen hinweg mit ihm:
1. **Interaktiver Text- & Sprachchat** mit anpassbarer Oberfläche, Live2D-/VRM-Avataren und Sprachanrufen in Echtzeit.
2. **Soul-Memory-Architektur** mit langfristiger emotionaler Entwicklung, einem persönlichen Tagebuch und selbstheilenden Gedächtnisprotokollen.
3. **Soul-Stage-RPG-Engine** für ein vollständiges Tabletop-Text-RPG, geleitet von einem eigenen KI-Spielleiter – mit Würfelwürfen und verborgenen Handlungsbögen.
4. **Soul Companion** – ein autonomer Agent, der auf deinem Bildschirm lebt und von einer neurohormonellen Simulation angetrieben wird. Ohne weitere Einrichtung kann er deinen Bildschirm sehen, Maus und Tastatur steuern, selbstständig im Web surfen, Code ausführen und deine Dateien ordnen. Du willst mehr? Schreib eigene Python-Plugins oder verbinde einen beliebigen externen MCP-Server, um ihm völlig neue Fähigkeiten zu geben. Jede riskante Aktion muss über ein Bestätigungsbanner auf dem Bildschirm freigegeben werden – nichts passiert ohne dein Okay.

Standardmäßig läuft alles **zu 100 % lokal auf deinem PC** – die Chats mit deinen Charakteren können komplett offline stattfinden, ohne Abos und ohne Filter. Cloud-KI-Anbieter (OpenAI, Claude, Gemini und weitere) stehen optional zur Verfügung, etwa für schwächere Hardware oder anspruchsvolleres Reasoning, und Browser-/Web-Werkzeuge greifen natürlich aufs Internet zu, wenn eine Aufgabe es erfordert – der Kern der App braucht aber nie ein Konto und schickt deine Daten nirgendwohin, ohne dass du es willst.

---

## 🆕 Neu seit Soul Trinity (v2.4.0)

Seit dem ursprünglichen Release von Soul Trinity (v2.4.0) hat sich Soul of Waifu schnell weiterentwickelt. Die Highlights:

- **Soul Companion ist jetzt ein vollwertiger autonomer Betriebssystem-Agent.** Er kann deine Maus bewegen, in jedes Fenster klicken und tippen, über einen echten Headless-Browser selbstständig im Web surfen, Python-/PowerShell-Skripte in einer Sandbox ausführen, deine Dateien ordnen und mehrstufige Aufgaben verketten – alles abgesichert durch ein Human-in-the-Loop-Bestätigungsbanner mit 25-Sekunden-Countdown, sodass nichts Riskantes ohne dein Okay passiert.
- **Soul Stage ist zu einem echten Tabletop-RPG-Simulator gewachsen.** Deterministische Würfelwürfe und Fertigkeitsproben, verborgene Story-Arcs, die deine Gruppe tatsächlich aufdecken muss, ein Live-Kampagnenbrett mit Druck-Uhren, strukturierte Beziehungsverfolgung, die keinen Groll und keine Bindung vergisst, und Szenenordner zum Organisieren ganzer Kampagnen.
- **Tool-Calling gibt es nicht mehr nur im Companion.** Websuche, Zugriff auf die Zwischenablage und App-Steuerung funktionieren jetzt auch in normalen 1:1-Text- und Sprachchats.
- **Das Discord-Gateway ist schlauer geworden.** Volles Computer Vision für Bilder und GIFs sowie ein Bewusstsein für einzelne Mitglieder, sodass es auf einem Server nie durcheinanderbringt, wer was gesagt hat.
> Das vollständige, detaillierte Änderungsprotokoll jeder Version findest du auf der [Releases-Seite](https://github.com/jofizcd/Soul-of-Waifu/releases).

---

## 🚀 Wichtigste Module & Fähigkeiten

### 1. Eine Seele, viele Dimensionen

Jeder Charakter, den du erschaffst, ist eine einzige durchgehende Identität, die sich durch mehrere verbundene Modi bewegt – dieselbe Persönlichkeit und dieselben Erinnerungen begleiten ihn überallhin.

| Modus | Beschreibung |
|---|---|
| 🧠 **Soul Memory** | Ein eigenständiges digitales Gehirn für jeden Charakter – verfolgt Stimmung, Beziehungen und gelebte Geschichte weit über eine einfache Stichwortsuche nach Fakten hinaus. |
| 💬 **Text- & Sprachchat** | Vollduplex-Unterhaltung mit Live2D- & VRM-Avataren, einem anpassbaren HUD für Zustandsvariablen, Lorebooks und Sprachanrufen in Echtzeit. |
| 🎲 **Soul Stage** | Ein vollständiges Tabletop-RPG unter einem virtuellen Spielleiter – Würfelwürfe, generierte Antwortoptionen, WorldState-Verfolgung, Inventar und dynamische NPCs mit eigenem Gedächtnis. |
| 🖥️ **Soul Companion** | Ein autonomer, neurohormonell gesteuerter Desktop-Agent – liest deinen Bildschirm, steuert Maus und Tastatur, surft selbstständig im Web, führt Code aus und ordnet deine Dateien; erweiterbar mit eigenen Plugins und MCP-Servern. |

---

### 🧠 Soul Memory — Langzeit-Gedächtnisarchitektur

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Soul-Memory-System" src="https://i.ibb.co/zH4fqtmC/sc-screenshots-soul-memory.png">
</p>

Übliche Vector-RAG-Ansätze durchsuchen alte Chatverläufe nach passenden Stichwörtern. **Soul Memory** arbeitet dagegen als autonomer Hintergrund-Agent, der vier voneinander getrennte kognitive Dateien laufend in Echtzeit neu schreibt:

- **Psychologie-Ebene**: Verfolgt aktuelle Stimmung, innere Anspannung, verborgene Motive und die Entwicklung des Charakters.
- **Beziehungsprofil**: Merkt sich Gewohnheiten und Vorlieben des Nutzers, gemeinsame Versprechen und die Entwicklung des Vertrauens.
- **Episodisches Themenarchiv**: Eine kategorisierte Wissensbasis, die Orte, Ereignisse und wichtige Fakten indiziert und über lokale semantische Embeddings mit deinen Anfragen abgleicht – mit hoher Genauigkeit in zwei Sprachen.
- **Persönliches Tagebuch**: Nachdenkliche Einträge in der Ich-Form, die der Charakter nach bedeutsamen Gesprächen schreibt.

> [!TIP]
> **Kognitive Mechaniken:**
> - **Emotionales Abklingen:** Groll und negative Stimmungsspitzen kühlen mit der Zeit von selbst ab, wenn sie nicht erneut aufgegriffen werden.
> - **Selbstheilendes Gedächtnis:** Das System erkennt logische Widersprüche zwischen neuen Antworten und früheren Fakten, überschreibt veraltete Informationen automatisch und protokolliert die Korrekturen.
> - **Duplikaterkennung:** Nahezu identische Erinnerungen werden automatisch zusammengeführt, damit das Archiv auch bei langer Nutzung sauber bleibt.
> - **Absturzsicheres Speichern:** Gedächtnis-Updates werden atomar gespeichert – ein unerwarteter Fehler mitten in der Sitzung kann deinen Charakter nicht mehr seine Erinnerungen kosten.

Wähle zwischen **Full Sync** (maximale Tiefe), **Soul Link** (ausgewogen), **Mind Spark** (leichtgewichtig) oder **Reflection Flow** (nur Tagebuch), passend zu deinem verfügbaren VRAM/RAM.

---

### 🎲 Soul Stage — Tabletop-RPG & Spielleiter-Engine

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Soul-Stage-RPG-Modus" src="https://i.ibb.co/Ld2VcVFS/sc-screenshots-soul-stage.png">
</p>

Soul Stage verwandelt deinen Chat in eine strukturierte Tabletop-Rollenspielkampagne, die von einem virtuellen Spielleiter geleitet wird. Der Spielleiter ist eine eigene KI-Ebene, die unabhängig von deinem Charakter läuft: Er verwaltet den Zustand der Welt, lenkt Ereignisse und sorgt für Struktur in Gruppen-Rollenspielsitzungen.

- **WorldState-Engine:** Strikte Verfolgung von Tageszeit, Wetter, aktuellem Ort und wichtigen Fakten im Spiel.
- **Würfelwürfe & Fertigkeitsproben:** Deterministische Mechaniken entscheiden über Aktionen, statt den Ausgang der Laune der KI zu überlassen.
- **Story-Arcs:** Verborgene Wendungen und Ermittlungen bleiben vor NPCs und der Gruppe geheim, bis im Spiel konkrete Hinweise gefunden werden.
- **Kampagnenbrett:** Ein Live-Zieltracker mit „Druck-Uhren“ – Alarmstufe der Wachen, Vertrauensanzeigen, Ritual-Countdowns –, die sich dynamisch mit deinen Entscheidungen verändern.
- **Zugsteuerung:** Wechsle zwischen den Eingabemodi Sagen, Tun, Denken und Regie, wähle den nächsten Sprecher manuell oder sende private Flüsternachrichten, die nur ein Gruppenmitglied sieht.
- **Strukturierte Beziehungsverfolgung:** Vertrauensstufen und soziale Rollen werden serialisiert und in jeden Zug eingespeist, sodass Gefährten und NPCs ihre Beziehung zu dir nie „vergessen“ – auch nicht Dutzende Züge später. Rollen und Titel können sich mitten in der Geschichte ändern, und das Verhalten passt sich sofort an.
- **Interaktive Gruppe & NPCs:** Die Hauptmitglieder der Gruppe synchronisieren ihre Erinnerungen über Soul Memory, während für bestimmte Begegnungen dynamische, temporäre NPCs (mit eigenem dauerhaftem Gedächtnis) erscheinen.
- **Inventar- & Status-HUD:** Verfolge Ausrüstung, Gesundheit, Energie, Stress, Zustände (vergiftet, erschöpft, inspiriert) und Gold in Echtzeit.
- **Szenenordner:** Organisiere deine Szenario-Bibliothek nach Kampagnen, Genres oder Settings.
- **Atmosphärische Automatik:** Hintergründe und Umgebungsgeräusche wechseln automatisch, wenn die Geschichte an neue Orte führt.
- **Ereigniskarten:** Karten für Zufallsbegegnungen halten Kampagnen unberechenbar.

---

### 🖥️ Soul Companion — Autonomer Desktop-Agent

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Soul-Companion-Desktop-Overlay" src="https://i.ibb.co/ZzgN6LDw/sc-screenshots-soul-companion.jpg">
</p>

Soul Companion macht deinen Charakter zu einem autonomen Bewohner deines Desktops – und seit dem neuesten Release zu einem echten Computer-Use-Agenten. Als transparentes Overlay bleibt der Companion bei dir, während du arbeitest, spielst oder surfst. Sein Verhalten wird von einem Neurohormonsystem (Dopamin, Cortisol, Oxytocin, Müdigkeit) gesteuert statt von simplen reaktiven Prompts: Er hat Stimmungen, die sich je nach Aktivität, Tageszeit und deinem Interaktionsverhalten verändern, wird nach langen Sitzungen müde, langweilt sich bei längerer Inaktivität und beginnt von sich aus ein Gespräch, wenn auf deinem Bildschirm etwas Bemerkenswertes passiert.

**Computer Use & Betriebssystem-Steuerung:**

| Werkzeug | Was es macht |
|---|---|
| 🖱️ **GUI-Aktionen** | Bewegt den Cursor, klickt (einfach/doppelt/rechts), scrollt, sendet Tastenkürzel und tippt Text direkt in jedes aktive Fenster (Discord, Editor, VS Code, Browser usw.) |
| 🌐 **Browser-Agent** | Ruft selbstständig URLs auf, extrahiert sauberen Artikeltext, klickt Buttons, füllt Formulare aus und lädt Dateien über einen echten Headless-Browser (Playwright) herunter |
| 🐍 **Code-Ausführung** | Schreibt und startet spontan Python-/PowerShell-Skripte in einer Sandbox (unter Linux Python/Bash) für Berechnungen, Datenauswertung oder Stapelaufgaben – mit strikten Zeitlimits |
| 📁 **Dateiorganisation** | Untersucht deinen Desktop und deine Ordner, sortiert herumliegende Dateien automatisch in Kategorien und bietet eine schnelle Dateinamensuche |
| 🧭 **Aufgabenplaner** | Wandelt ein komplexes, gesprochenes Ziel in eine mehrstufige Werkzeugkette um und führt sie komplett aus |
| ❤️‍🩹 **System-Wächter** | Warnt dich vorausschauend vor niedrigem Akkustand, überhitzter GPU oder abgeschlossenen Downloads |
| 🔎 Bildschirmleser | Sieht deinen Bildschirm und kommentiert, analysiert oder hilft bei dem, was zu sehen ist |
| 📋 Zwischenablage | Liest kopierten Text auf Wunsch und verarbeitet ihn |
| 🔍 Websuche | Sucht Informationen in Echtzeit |
| 🎵 Musiksteuerung | Steuert die Audiowiedergabe |
| 🔌 Eigener MCP-Server | Verbinde einen beliebigen externen MCP-Server für zusätzliche Integrationen |

**Sicherheit von Grund auf:** Jede potenziell riskante Aktion – Dateien verschieben, Code ausführen, Maus oder Tastatur steuern – wird von einem Bestätigungsbanner auf dem Bildschirm mit 25-Sekunden-Countdown abgefangen. Nichts wird ohne deine ausdrückliche Bestätigung ausgeführt, und die App gibt danach den Fokus automatisch an dein aktives Fenster zurück, damit keine Tastenanschläge verloren gehen.

---

### 📊 Eigene Zustandsvariablen & adaptives HUD

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="HUD für eigene Zustandsvariablen" src="https://i.ibb.co/rKVFcMY1/sc-screenshots-hud.png">
</p>

Baue Dating-Sims, RPG-Wertesysteme oder Tamagotchi-Mechaniken direkt in Charakterkarten – ganz ohne Code.
- **Adaptive HUD-Leiste:** Zeigt oben im Chat animierte Fortschrittsbalken (`int`), JA/NEIN-Abzeichen (`bool`), Gegenstandslisten (`list`) oder Textlabels (`str`) an.
- **Robuster KI-Interceptor:** Ein Backend-Interceptor liest Zustandsänderungen zuverlässig aus, sodass Updates auch bei JSON-Tippfehlern des LLM funktionieren.
- **11 eingebaute Vorlagen:** Sofort nutzbare Vorlagen für Romance, RPG, Survival, Verhör, Horror und Visual Novels.

---

## 🌐 Ökosystem & erweiterte Integrationen

### 📱 Lokaler Web-Client (Zugriff per Smartphone / Tablet)

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Oberfläche des Web-Clients" src="https://i.ibb.co/G3cgzpFq/sc-screenshots-web-server.png">
</p>

Starte Soul of Waifu auf deinem Haupt-PC und verbinde dich im Heim-WLAN von Smartphone oder Tablet über `http://<ip-deines-pcs>:8000`. Mit bidirektionaler WebSocket-Synchronisierung in Echtzeit, eigenen Chat-Hintergründen, Avatar-Darstellung und Spracheingabe, die direkt über das lokale Faster-Whisper-Modell deines PCs läuft.

---

### 🤖 Discord-Gateway

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Discord-Gateway" src="https://i.ibb.co/xtRJ4y83/sc-screenshot-discord.png">
</p>

Verbinde deine Soul-of-Waifu-Charaktere direkt mit Discord-Bots. Chatte mit ihnen in Serverkanälen oder Privatnachrichten – mit ihrer vollen Persönlichkeit, ihren Systemprompt-Einstellungen und ihrem Langzeitgedächtnis.
- **Mehrbenutzer-Bewusstsein auf Servern:** Unterscheidet zwischen einzelnen Servermitgliedern und führt für jeden Sprecher einen eigenen Gesprächskontext.
- **Computer Vision:** Sieht, untersucht und reagiert auf Bilder und GIFs in Direktnachrichten oder Serverkanälen.

---

### 🎨 KI-Bildgenerierung

<p align="center">
  <img style="width:90%; border-radius: 8px;" alt="Bildgenerierung im Chat" src="https://i.ibb.co/sv4DqPQ0/sc-screenshot-image-gen.png">
</p>

Erzeuge Illustrationen direkt in Chatnachrichten über das Kontextmenü.
- **Lokale Engines:** Automatic1111 WebUI, ComfyUI API.
- **Cloud-Engines:** NovelAI Diffusion, DALL-E 3, FLUX.
- Erstellt automatisch passende Bild-Prompts auf Basis von Aussehen, aktueller Pose, Gefühlslage und Umgebung des Charakters.

---

## 🛠️ Technik im Detail & Feintuning

<details>
<summary><b>🎙️ Stimme, Spracherkennung & Avatare</b></summary>

- **6 Text-to-Speech-Engines:**
  - **Qwen3 TTS (lokal):** Extrem geringe Latenz, Stimmklonen aus einer 3-Sekunden-Audioprobe, Stimmdesign per Prompt, 9 eingebaute Sprecher, Modelle mit 1,7B und 0,6B.
  - **XTTSv2 & Kokoro 82M (lokal):** Hochwertige Sprachsynthese und Zero-Shot-Stimmklonen.
  - **Silero TTS (lokal):** Schnelle Engine für russische Stimmen.
  - **EdgeTTS & ElevenLabs (Cloud):** Hochwertige neuronale Cloud-Stimmen.
- **RVC-Unterstützung:** Integrierte Einstellungen für Voice Conversion (Tonhöhenverschiebung, Index-Rate, Schutz).
- **Satzweises Streaming:** Die Wiedergabe startet schon beim ersten generierten Satz – ohne Verzögerung bei der Antwort.
- **Vollduplex-Anrufe (SoW System):** Silero VAD (Sprachaktivitätserkennung) + Faster-Whisper-Transkription mit nahtloser Unterbrechung durch den Nutzer.
- **Avatare & Klassifikator für 28 Emotionen:** Live2D (mit verknüpften Bewegungsanimationen), VRM-3D-Modelle, GIFs und statische Bilder. Automatische Gefühlsanalyse mit 28 Zuständen und Lippensynchronisation zum Audio.

</details>

<details>
<summary><b>🎛️ Erweitertes Text-Sampling (gegen Wiederholungsschleifen)</b></summary>

- **Dynamische Temperatur:** Passt die Temperatur je nach Konfidenz an, um Kreativität und Logik auszubalancieren.
- **DRY-Sampler (Don't Repeat Yourself):** Verhindert Schleifen aus mehreren Wörtern, ohne die Grammatik zu verschlechtern.
- **XTC (Exclude Top Candidates):** Filtert überstrapazierte KI-Klischees und sich wiederholendes Vokabular heraus.
- **Min-P:** Schneidet Tokens mit geringer Wahrscheinlichkeit relativ zum Top-Kandidaten ab, für eine stimmige Ausgabe.

</details>

<details>
<summary><b>📖 Überarbeitete Lorebook-Engine</b></summary>

- **Mehrfachbindung:** Verknüpfe mehrere Lorebooks gleichzeitig mit einem Charakter.
- **Semantischer Situationsabgleich:** Eine lokale Vektorsuche wählt Lore-Einträge nach dem Kontext der Situation statt nach starren Stichwörtern aus.
- **Szenenspannungs-Akkumulator:** Baut dynamisch erzählerische Energie auf, um Zufallsereignisse auszulösen.
- **Kettenabhängigkeiten:** Erstelle mehrstufige Questreihen mit zeitversetzt freigeschalteten Einträgen.
- **Einfügemodi:** Wähle zwischen *Passiv (Hintergrundwissen)* und *Aktiv (Systemanweisung)*.

</details>

<details>
<summary><b>💻 Lokale & Cloud-LLM-Backends</b></summary>

- **Unterstützung für Reasoning-Modelle:** Eigene Einstellung für das Budget an Denk-Tokens und automatisches Auslesen von `<think>`-Blöcken bei Reasoning-Modellen wie DeepSeek.
- **Models Hub:** Integrierte Suche in Hugging-Face-Repositories, GGUF-Downloader mit Fortschrittsbalken und sofortigem Abbruch sowie automatischer Updater für die Llama.cpp-Binärdateien.
- **Lokale Beschleunigung:** Llama.cpp-HTTP-Server mit Unterstützung für **CUDA (NVIDIA)**, **HIP (AMD)**, **SYCL (Intel)** und **Vulkan**.
- **Leistungsoptionen:** Flash Attention, MLock, KV-Cache-Quantisierung (`q8_0`, `q4_0`), Denkmodus und Auslagern von MoE-Schichten auf die CPU.
- **10 Cloud-Anbieter:** OpenRouter, OpenAI, Anthropic Claude, DeepSeek, Grok (xAI), Google Gemini, Qwen, Mistral AI, Z.AI, Player2 sowie eigene OpenAI-kompatible Endpunkte.

</details>

---

## 📥 Installation

### Windows

Keine Python-Kenntnisse, kein Node.js und keine Erfahrung mit der Kommandozeile nötig.

```
1. Lade das neueste Release-Archiv (derzeit Soul-of-Waifu-v2.5.1.rar) unter „Releases“ herunter.
2. Entpacke es mit 7-Zip oder WinRAR in einen Pfad ohne Leerzeichen und ohne kyrillische Zeichen (z. B. C:\AI\Soul-Of-Waifu\).
3. Starte installer.bat (NICHT als Administrator ausführen).
4. Starte das Programm über start.bat.
```

> [!WARNING]
> **Führe `installer.bat` nicht als Administrator aus!** Windows setzt das Arbeitsverzeichnis von Administrator-Prozessen auf `C:\Windows\System32`, was zu Fehlern bei den Installationspfaden führt. Starte die Datei mit einem normalen Doppelklick.

### 🐧 Linux

Dieser Fork enthält eine Linux-Portierung im Branch `linux`. Der Installer richtet Python 3.11, PyTorch
(CUDA/ROCm/CPU), llama.cpp und alle Abhängigkeiten ein und holt die Programmdateien aus dem offiziellen
Release-Archiv:

```bash
git clone -b linux https://github.com/SnowwhiteOakheart/Soul-of-Waifu.git
cd Soul-of-Waifu
./installer.sh     # danach starten mit ./start.sh
```

Systempakete, GPU-Backends und den Stand der einzelnen Funktionen findest du in **[README-LINUX.md](README-LINUX.md)**.

### Systemanforderungen

| | Minimum | Empfohlen |
|---|---|---|
| **Betriebssystem** | Windows 10/11 (64 Bit) oder Linux (x86_64) | Windows 10/11 (64 Bit) oder Linux (x86_64) |
| **RAM** | 8 GB | 16 GB+ |
| **GPU** | Beliebig (für Cloud-APIs) | NVIDIA / AMD mit 6+ GB VRAM (für lokale Modelle) |
| **Speicher** | 10 GB freier Speicherplatz | Schnelle NVMe-SSD |

---

## ⚡ Schnellstart

- **Option A — Cloud-KI (keine GPU nötig):**
  Öffne **Optionen -> Konfiguration** und gib deinen API-Schlüssel für OpenRouter oder OpenAI ein. Importiere eine Charakterkarte aus dem **Characters Gateway** oder ziehe eine `.png`- / `.json`-Datei per Drag & Drop ins App-Fenster.
- **Option B — Lokale KI:**
  Öffne den **Models Hub**, suche nach einem Modell (z. B. `Gemma` oder `Qwen`) und lade eine GGUF-Quantisierung `Q4_K_M` herunter. Wähle unter **Optionen -> LLM-Einstellungen** dein GPU-Backend (CUDA/HIP/SYCL/Vulkan), aktiviere Flash Attention und starte den Server über den Models Hub.

Sobald alles eingerichtet ist, stehen Websuche, Zugriff auf die Zwischenablage, App-Steuerung und weitere Werkzeuge direkt in normalen Text- und Sprachchats zur Verfügung – dafür musst du nicht in den Soul-Companion-Modus wechseln.

Unter **Optionen** kannst du die Programmsprache auf **Deutsch** umstellen (Neustart erforderlich).

📖 Vollständige Dokumentation & Anleitungen (Englisch): **[jofizcd.github.io/soul-of-waifu-site/docs](https://jofizcd.github.io/soul-of-waifu-site/docs/)**

---

## 💖 Unterstützung & Community

Soul of Waifu ist ein Open-Source-Projekt eines einzelnen Entwicklers. Alle Funktionen sind zu 100 % kostenlos – ohne Bezahlschranken oder Premium-Stufen.

**Finanzielle Unterstützung:**
- **[Boosty](https://boosty.to/jofizcd)**
- **[Donation Alerts](https://www.donationalerts.com/r/jofizcd)**

**Community & Hilfe:**
- **Gib diesem Repository einen Stern** – das erhöht die Sichtbarkeit auf GitHub!
- **Tritt unserem [Discord-Server](https://discord.com/invite/6vFtQGVfxM) bei** – teile eigene Charakterkarten, Lorebooks und RPG-Szenen und hol dir Hilfe aus der Community.

---

## 📊 Repository-Statistik

<div align="center">
  <img src="https://star-history.dera.page/svg?repos=jofizcd/Soul-of-Waifu&type=Date" alt="Verlauf der GitHub-Sterne"/>
</div>
<br>
<div align="center">
  <img src="https://repobeats.axiom.co/api/embed/6af186be156d185ec7424197ff77edf14db5eeb0.svg" alt="Repobeats-Analyse">
</div>

---

## 👤 Entwickler

<div align="center">
  <a href="https://github.com/jofizcd">
    <img style="border-radius: 50%;" width="110" src="https://i.ibb.co/Hj3g4j2/ava.jpg" alt="Avatar von Jofi">
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
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="Lizenz: GPL v3">
  </a>
</p>
