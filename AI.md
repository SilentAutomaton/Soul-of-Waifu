# AI Context & Technical Handbook: Soul of Waifu (Linux Port)

> **Zweck dieser Datei:** Diese Datei dient KIs und Entwicklern als zentraler Leitfaden und Architektur-Überblick für den **Linux-Port von Soul of Waifu**. Sie dokumentiert die Fork-Struktur, die Patch-Philosophie, wichtige Werkzeuge und Verhaltensregeln.

---

## 1. Projekt-Identität & Fork-Modell

* **Projektname:** Soul of Waifu (Linux Port & German Preset Set)
* **GitHub:** `SnowwhiteOakheart/Soul-of-Waifu` (Branch: `linux`)
* **Upstream:** `https://github.com/jofizcd/Soul-of-Waifu`
* **Lizenz:** GPL-3.0

### Branch-Struktur
| Branch | Inhalt |
|---|---|
| `release` | **Unveränderter** offizieller Upstream-Release-Quellcode (z. B. v2.5.1). Dient als neutrale Diff-Basis. |
| `linux` | Der eigentliche Linux-Port mit allen 41 Patches, Werkzeugen und deutschen Presets (Standard-Branch). |
| `main` | Upstreams GitHub-Zweig (unberührt). |

---

## 2. Das Wichtigste für KIs: Die Patch-Integrität

> [!IMPORTANT]
> Vor und nach jeder Code-Änderung an Upstream-Dateien **MUSS** `./tools/fork_report.sh` ausgeführt werden.
> Es prüft automatisch alle 41 Patches auf Anwesenheit und meldet eventuelle Regressionen.

### Schlüssel-Module des Ports:
1. **`app/utils/platform_compat.py`:** Linux-Äquivalente für Windows-Calls (`open_path`, `reveal_path`, `get_idle_time_ms`, kein `os.startfile` oder `ctypes.windll`).
2. **`app/utils/sfx_manager.py`:** Prozedurale RPG-Soundeffekte (Würfelrollen, Settle, Critical Fanfares, Fehlschläge, Tränke, Lagerfeuer-Ambiente) via `numpy` und `sounddevice`.
3. **`tools/fork_report.sh`:** Verifiziert alle Patches gegen die Liste in `FORK-CHANGES.md`.
4. **`tools/fetch_llama_backend.py`:** Lädt vorkompilierte Ubuntu/Linux llama.cpp Binaries herunter.
5. **`tools/fetch_live2d_models.py`:** Lädt Cubism 3/4 Live2D-Modelle herunter und entpackt sie nach `assets/emotions/live2d/`.
6. **`tools/import_character_cards.py`:** Importiert `chara_card_v2` Karten, Lorebooks, Soul-Stage-Szenen und deployt Hintergründe automatisch. Unterstützt `--update-live2d`, `--update-avatars` und `--update-scenes`.

---

## 3. Architektur & Dateistruktur

```text
/home/deathtrap/development/Soul-of-Waifu-linux/
├── app/
│   ├── configuration/         # Konfigurationen & aktive Charakter-Shards (characters/*.json)
│   ├── gui/                   # PySide6 GUI (chat_page, soul_stage_page, interface_signals)
│   │   ├── soul_stage_page.py # Soul Stage RPG (HUD, Clocks, Dice, Camp, Inventar, CombatBar)
│   │   └── interface_signals.py # Signale, Turn-Management, Audio/TTS & Event-Dispatch
│   ├── translations/          # Lokalisierung (de.yaml, en.yaml, ru.yaml)
│   └── utils/                 # Platform-Compat, Local-Server-Manager, SFXManager, Audio, Live2D
│       └── sfx_manager.py     # Prozedurale RPG-Soundeffekte (Würfel, Camp, Items)
│
├── assets/
│   ├── backgrounds/           # Globale Chat- & Soul-Stage-Hintergründe (16:9 PNG/JPG)
│   └── emotions/live2d/       # Entpackte Live2D-Modelle (unitychan, haru, senko, rice etc.)
│
├── presets/
│   └── sakura-succubus-3/     # Deutsche Referenz-Preset-Sammlung
│       ├── backgrounds/       # 9 x 16:9 Anime-Hintergründe für Szenen & Lore
│       ├── lorebooks/         # 3 Lorebooks (Welt, Figuren, Orte)
│       ├── scenes/            # 6 Soul-Stage-Szenen
│       └── *.json             # 7 Charakterkarten (inkl. Live2D-Mapping & Avatare)
│
├── tools/
│   ├── fork_report.sh         # Patch-Checker & Diff-Reporter
│   ├── fetch_live2d_models.py # Live2D Modell-Downloader
│   ├── fetch_llama_backend.py # llama.cpp Linux Downloader
│   └── import_character_cards.py # Bulk-Importer für Karten, Szenen & Hintergründe
│
├── FORK-CHANGES.md            # Ausführliche Dokumentation aller Patches & Fork-Änderungen
├── README-LINUX.md            # Installations- und Betriebsanleitung für Linux
├── Roadmap.md                 # Soul Stage RPG Roadmap (Phasen 1 bis 5 abgeschlossen)
└── AI.md                      # Dieser Leitfaden
```

---

## 4. Konventionen für AIs

1. **Anrede:** Sprich den Benutzer immer mit **Du** (informell) an.
2. **Pfade:** Nutze unter Linux immer `/` statt `\\`. Pfade zu Assets dürfen niemals feste Backslashes enthalten.
3. **Upstream-Sauberkeit:** Änderungen an Kern-Dateien so minimal und defensiv wie möglich halten, damit zukünftige Upstream-Merges konfliktfrei bleiben.
4. **Venv-Nutzung:** Python-Befehle immer mit der Projekt-Venv ausführen: `app/data/envs/sow/bin/python`.
