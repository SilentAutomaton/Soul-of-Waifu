# 🎲 Soul Stage RPG — Verbesserungs-Roadmap

Diese Roadmap bündelt die Weiterentwicklung der **Soul Stage Tabletop-RPG-Engine** in Soul of Waifu in fünf fokussierten Phasen, um das Spielerlebnis noch immersiver, responsiver und lebendiger zu machen.

---

## Übersicht der Phasen

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                              SOUL STAGE EVOLUTION ROADMAP                                   │
└───────┬─────────────────────┬─────────────────────┬──────────────────┬──────────────────┬──┘
        │                     │                     │                  │                  │
        ▼                     ▼                     ▼                  ▼                  ▼
   [Phase 1]             [Phase 2]             [Phase 3]          [Phase 4]           [Phase 5]
   Live-HUD &            Audio & TTS-          Player Agency &    Rast- & Camp-       Taktischer
   Sichtbarkeit          Atmosphäre            RPG-Entscheidungen Mechanik            Begegnungs-Modus
   (HP, Stress, Uhren)   (Würfel-SFX & Voice)  (Proben & Tags)    (Erholung & Bond)   (Initiative & Kampf)
```

---

## 📌 Phase 1: Live-HUD & Sichtbarkeit (HP, Energie, Stress, Zustände, Uhren)
> **Ziel:** Alle im Hintergrund bereits berechneten RPG-Zustände für den Spieler direkt im Spielfeld sichtbar und spürbar machen.

- [x] **1.1 Live-Ressourcen- & Status-Leiste (Player HUD):**
  - Anzeige von **HP** (z. B. `10/10`), **Energie** (`6/6`) und **Stress** (`0/6`) direkt über oder neben der Eingabeleiste im Chat.
  - Dynamische **Status-Badges** für aktive Zustände (z. B. 🩸 *Blutend [3]* oder 🧪 *Vergiftet [2]*) inklusive Tooltips mit Restdauer und Effekt.
  - Optisches Feedback (Pulsieren / Animation bei Schaden, Heilung oder Stress-Zunahme).
- [x] **1.2 Mini-Tracker für Uhren & Quests:**
  - Einklappbares Seiten-Panel oder kompaktes Widget für aktive *Campaign Clocks* (z. B. `Wachen alarmiert: 2/4`) und offene *Objectives*.
  - Visueller Fortschritt (Segmente/Progress-Bar), der sofort tickt, wenn der GM eine Uhr weiterschaltet.
- [x] **1.3 Narrativer Ereignis-Banner (Toasts im Chat):**
  - Große Ereignisse (Freischaltung eines Story Arcs, dauerhafte Konsequenz im Ledger) erhalten eine visuell ansprechende Event-Card im Chatverlauf.

---

## 📌 Phase 2: Audio & TTS-Atmosphäre (Soundeffekte & Sprachausgabe)
> **Ziel:** Das textlastige Geschehen durch dynamische Soundeffekte und Sprachausgabe zum Leben erwecken.

- [x] **2.1 RPG-Soundeffekte (SFX):**
  - **Würfel-Sound:** Echtes Würfelgeräusch während der `SoulStageDiceCard`-Animation.
  - **Erfolgs- / Patzer-Jingles:** Befriedigender Chime bei Erfolg / Natural 20, dumpfer Sound bei Fehlschlag.
  - **Atmosphärische Stingers & UI-Sounds:** Sound bei Kampfeintritt (`encounter`), Entdeckungen oder Item-Nutzung.
- [x] **2.2 TTS-Integration für Begleiter & Erzähler:**
  - Anbindung an bestehende TTS-Engines (Edge-TTS, Fish Speech, etc.).
  - Jeder Party-Begleiter spricht automatisch mit seiner konfigurierten Stimme.
  - Optionaler Erzähler-Sprecher mit tiefer, ruhiger Erzählstimme.
  - Kleiner "Vorlesen / Audio"-Button an jeder Chatblase zum manuellen Abspielen.

---

## 📌 Phase 3: Spieler-Handlungsmacht & RPG-Entscheidungen
> **Ziel:** Dem Spieler aktive Eingriffsmöglichkeiten in das Regelwerk geben und Antwortmöglichkeiten vertiefen.

- [x] **3.1 Aktive Spieler-Würfelproben (Manual Dice Roller):**
  - Button an der Eingabeleiste (🎲 *Würfeln / Probe*).
  - Menü zur Auswahl: Freier W20/W100/W6/2W6/W12 oder gezielte Fertigkeitsprobe (`Heimlichkeit (+3) vs DC 12`).
  - Das Würfelergebnis wird animiert im Chat gerollt, mit SFX untermalt und fließt automatisch als Kontext in die Runde ein.
- [x] **3.2 Erweiterte Antwortoptionen mit Skill- & Ressourcen-Tags:**
  - Prompt-Anpassung für den GM Planner: Antwortoptionen erhalten strukturierte Tags wie `[Heimlichkeit +3]`, `[Überzeugen +1 | DC 13]`, `[-1 Energie]`.
  - Optische Darstellung in der `ChoicesBar` mit farbigen Badges (Amber für Proben/DCs, Cyan für Kosten).
- [x] **3.3 Interaktives Inventar 2.0 mit Sofort-Effekten:**
  - Verbrauchsgegenstände (z. B. Heiltrank, Brot, Bandage, Gegengift) heilen bei Klick direkt HP/Energie/Stress, heilen Zustände aus und werden aus dem Inventar entfernt.
  - Automatische Erstellung einer Event-Card und Speicherung im Spielstand.

---

## 📌 Phase 4: Rast- & Campfire-Mechanik (Erholung & Gruppen-Dynamik)
> **Ziel:** Sinnvolle Regeneration von Ressourcen und intime Charakter-Interaktionen abseits der Action.

- [x] **4.1 Rast-Aktion ("Lager aufschlagen"):**
  - Button in der Top-Bar (🏕️ *Rast / Camp*).
  - Auswahl zwischen *Kurzer Rast* (+3 Energie, +2 HP) und *Langer Rast* (volle HP 10/10, volle Energie 6/6, Stress 0/6, Kuriert alle Statuseffekte).
- [x] **4.2 Campfire-Interlude & Gruppen-Banter:**
  - Optionale Checkbox für einen automatischen Trigger einer atmosphärischen Lagerfeuer-Szene.
  - Begleiter unterhalten sich ungezwungen untereinander am Feuer, reflektieren Erlebnisse und vertiefen die Stimmung.
- [x] **4.3 Beziehungs-Meilensteine (Bond Levels):**
  - Erhöhung der Zuneigung am Lagerfeuer (+5 bei Langer Rast, +2 bei Kurzer Rast).
  - Automatische Erkennung von Schwellenwerten (+25, +50, +75) und Auslösen von *Bond Milestone*-Benachrichtigungen im Chat.

---

## 📌 Phase 5: Taktischer Begegnungs-Modus
> **Ziel:** Ein leichtgewichtiges Kampfsystem, das physische Konfrontationen greifbar und taktisch macht, ohne die erzählerische Tiefe der Engine durch ein volles Grid-Kampfsystem zu ersetzen.

- [x] **5.1 Initiative-Leiste & Gegner-HP:**
  - Sobald der GM ein `encounter` mit benannten, kampffähigen Gegnern auslöst, würfelt die Engine automatisch eine Initiative-Reihenfolge (Spieler, Begleiter, Gegner) und zeigt sie live über der Eingabeleiste an.
  - Jeder Gegner erhält eine eigene HP-Leiste (`4/10`), die bei Treffern durch den GM in Echtzeit sinkt; besiegte Gegner werden durchgestrichen markiert.
  - Nachrückende Verstärkung wird nahtlos in die laufende Initiative-Reihenfolge eingereiht.
- [x] **5.2 Schnellaktions-Buttons (Angriff, Ausweichen, Item, Flucht):**
  - Vier kontextsensitive Buttons erscheinen nur während eines aktiven Kampfes: 🗡️ *Angriff*, 🛡️ *Ausweichen*, 🎒 *Item* (öffnet das interaktive Inventar) und 🏃 *Flucht*.
  - Jede Aktion sendet einen getaggten Vorschlag (`[Attack] *I attack!*`), den der GM narrativ auflöst — inklusive Würfelprobe, Schaden und ggf. Kampfende.
- [x] **5.3 Kampfende & Auflösung:**
  - Der GM markiert das Ende eines Kampfes explizit (Sieg, Flucht geglückt, Waffenstillstand) oder die Engine erkennt automatisch, wenn alle Gegner besiegt sind.
  - Ein Ereignis-Kärtchen im Chat fasst Kampfbeginn, Verstärkung und Kampfende sichtbar zusammen, inklusive Sound-Stinger.

