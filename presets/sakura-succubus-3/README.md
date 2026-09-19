# Sakura Succubus 3 - character cards (German)

Seven ready-made cards for the visual novel *Sakura Succubus 3*: six characters and one user
persona. The texts are **German**, because they were written for the German UI of this fork.

| File | Who |
|---|---|
| `ayu_tatekawa.json` | Ayu - the tsundere pop idol |
| `marina_yamamoto.json` | Marina - the corporate CEO |
| `cosmos.json` | Cosmos - the playful cat girl |
| `hazel_williams.json` | Hazel - the tomboy tennis pro |
| `hifumi_minamoto.json` | Hifumi - the Yamato Nadeshiko |
| `yue.json` | Yue - the dethroned succubus queen |
| `persona_hiroki.json` | Hiroki as a **user persona** - who *you* are in the chat |

Each card carries description, personality, scenario, one greeting plus two alternate greetings
(the app offers them as variants of the first message) and three example dialogues. `{{user}}` and
`{{char}}` are filled in by the app, so the cards are not hard-wired to the name "Hiroki".

The files are plain **chara_card_v2** JSON and work in SillyTavern, Chub and anything else that
reads that format. Every card points at its `<name>.png` next to it through
`extensions.sow_avatar`, relative to the card, so the folder can be copied anywhere.

## Importing

All of them at once, including the persona:

```bash
app/data/envs/sow/bin/python tools/import_character_cards.py presets/sakura-succubus-3 \
    --persona presets/sakura-succubus-3/persona_hiroki.json
```

Characters that already exist are left alone. `--update-avatars` then refreshes only their picture
and keeps chats and settings; `--replace` overwrites the whole character and deletes its chats.
`--dry-run` shows what would happen. Single cards can also be imported in the app itself, under
**Create character -> Import character card**.

## About the pictures

The avatars are **AI generated** from the prompts in [AVATAR-PROMPTS.md](AVATAR-PROMPTS.md). They
show original characters described by archetype - a blonde idol with twintails, a CEO in a suit, a
cat girl in a maid uniform and so on - and use no artwork, sprite or reference image from the game.
The game's own art stays where it is, inside its archives.

License of the cards and pictures: same as the rest of this repository (GPL-3.0). *Sakura Succubus*
is a trademark of its publisher; this is unofficial fan content and not affiliated with them.
