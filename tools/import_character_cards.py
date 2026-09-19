#!/usr/bin/env python3
"""
Imports character cards (chara_card_v2 JSON), lorebooks and Soul Stage scenes into the
app's configuration, without clicking through the UI - useful for a whole set at once.

    app/data/envs/sow/bin/python tools/import_character_cards.py CARDS/ --persona CARDS/persona_hiroki.json

It writes through the app's own ConfigurationCharacters/ConfigurationSettings, so the
result is exactly what the character editor would have produced. Existing characters are
kept (their chats would be lost), unless --replace is given.

A persona file holds the user's own personas (the app calls them personas; they are edited
under Options -> Personas):

    {"personas": [{"user_name": "...", "user_description": "...", "user_avatar": null,
                   "default": true}]}

Cards are read the same way the app reads them: {"data": {...}} or a flat object, with
`first_mes`/`first_message` and `mes_example`/`example_messages` both accepted.
"""

import argparse
import datetime
import json
import re
import shutil
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.configuration.configuration import ConfigurationCharacters, ConfigurationSettings  # noqa: E402

CONFIG_FILES = ("app/configuration/characters.json", "app/configuration/settings.json",
                ".soul_stage/scenes.json")
SCENES_FILE = ROOT / ".soul_stage" / "scenes.json"


def read_card(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    data = raw.get("data", raw)
    if not data.get("name"):
        raise ValueError(f"{path.name}: the card has no name")
    avatar = data.get("extensions", {}).get("sow_avatar")
    if avatar:
        avatar = Path(avatar).expanduser()
        if not avatar.is_absolute():          # relative to the card, so a folder can be moved
            avatar = path.parent / avatar
    return {
        "name": str(data["name"]).strip(),
        "title": str(data.get("extensions", {}).get("sow_title") or data.get("title") or "").strip(),
        "description": str(data.get("description", "")).strip(),
        "personality": str(data.get("personality", "")).strip(),
        "scenario": str(data.get("scenario", "")).strip(),
        "first_message": str(data.get("first_mes") or data.get("first_message") or "").strip(),
        "example_messages": str(data.get("mes_example") or data.get("example_messages") or "").strip(),
        "alternate_greetings": [str(g).strip() for g in data.get("alternate_greetings", []) if str(g).strip()],
        "avatar": str(avatar) if avatar else None,
    }


def cache_avatar(source, character_name: str) -> str:
    """Copies an avatar into app/cache/avatars, exactly like the character editor does."""
    src = Path(source).expanduser()
    if not src.is_file():
        raise FileNotFoundError(src)
    dest_dir = ROOT / "app" / "cache" / "avatars"
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", character_name)
    dest = dest_dir / f"{safe}_avatar{src.suffix.lower() or '.png'}"
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    return f"app/cache/avatars/{dest.name}"


def backup_configs() -> None:
    for rel in CONFIG_FILES:
        src = ROOT / rel
        if src.exists():
            shutil.copy2(src, src.with_suffix(src.suffix + ".bak"))


def import_personas(path: Path, settings: ConfigurationSettings) -> list:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("personas", payload if isinstance(payload, list) else [payload])
    for entry in entries:
        raw_avatar = entry.get("user_avatar")
        if raw_avatar and not Path(raw_avatar).expanduser().is_absolute():
            entry["user_avatar"] = str(path.parent / raw_avatar)
    personas = settings.get_user_data("personas") or {}
    added = []
    for entry in entries:
        name = str(entry["user_name"]).strip()
        avatar = entry.get("user_avatar")
        if avatar:
            avatar = cache_avatar(avatar, name + "_persona")
        personas[name] = {
            "user_name": name,
            "user_description": str(entry.get("user_description", "")).strip(),
            "user_avatar": avatar,
        }
        added.append((name, bool(entry.get("default"))))
    settings.update_user_data("personas", personas)
    for name, is_default in added:
        if is_default:
            settings.update_user_data("default_persona", name)
    return added


def json_files(paths) -> list:
    out = []
    for raw in paths:
        path = Path(raw).expanduser()
        out += sorted(path.glob("*.json")) if path.is_dir() else [path]
    return out


def import_lorebooks(paths, settings, replace: bool) -> int:
    """A lorebook file is the lorebook itself: {name, description, n_depth, entries[]}."""
    books = settings.get_user_data("lorebooks") or {}
    added = 0
    for path in json_files(paths):
        book = json.loads(path.read_text(encoding="utf-8"))
        name = str(book.get("name") or path.stem).strip()
        if name in books and not replace:
            print(f"  lorebook already there, kept: {name}")
            continue
        raw_entries = book.get("entries", [])
        book["entries"] = list(raw_entries.values()) if isinstance(raw_entries, dict) else list(raw_entries)
        book["name"] = name
        settings.update_lorebook(name, book)
        print(f"  lorebook: {name}  ({len(book['entries'])} entries)")
        added += 1
    return added


def import_scenes(paths, replace: bool, known_characters, known_lorebooks) -> int:
    """Soul Stage stores its scenes in .soul_stage/scenes.json, keyed by a uuid."""
    data = {"scenes": {}, "scene_groups": {}}
    if SCENES_FILE.exists():
        data = json.loads(SCENES_FILE.read_text(encoding="utf-8")) or data
    data.setdefault("scenes", {})
    data.setdefault("scene_groups", {})

    by_title = {v.get("title"): k for k, v in data["scenes"].items()}
    now = datetime.datetime.now().isoformat()
    added = 0

    for path in json_files(paths):
        scene = json.loads(path.read_text(encoding="utf-8"))
        title = str(scene.get("title") or "").strip()
        if not title:
            print(f"  skipped {path.name}: the scene has no title")
            continue
        if title in by_title and not replace:
            print(f"  scene already there, kept: {title}")
            continue

        for member in scene.get("party", []):
            if member not in known_characters:
                print(f"  ! {title}: no character named '{member}' - import its card first")
        for book in scene.get("lorebook", []):
            if book not in known_lorebooks:
                print(f"  ! {title}: no lorebook named '{book}'")

        scene.setdefault("created_at", now)
        scene.setdefault("last_played", "")
        scene.setdefault("chat_log", [])
        sid = by_title.get(title) or str(uuid.uuid4())
        data["scenes"][sid] = scene
        print(f"  scene: {title}  ({scene.get('gm_tone', '?')}, party: {', '.join(scene.get('party', [])) or 'solo'})")
        added += 1

    if added:
        SCENES_FILE.parent.mkdir(parents=True, exist_ok=True)
        SCENES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return added


def main() -> int:
    parser = argparse.ArgumentParser(description="Import character cards into Soul of Waifu.")
    parser.add_argument("paths", nargs="*", help="card files, or folders holding them")
    parser.add_argument("--lorebooks", nargs="+", metavar="PATH", default=[],
                        help="lorebook files, or folders holding them")
    parser.add_argument("--scenes", nargs="+", metavar="PATH", default=[],
                        help="Soul Stage scene files, or folders holding them")
    parser.add_argument("--persona", metavar="FILE", help="persona file to import as well")
    parser.add_argument("--persona-name", metavar="NAME",
                        help="preselect this persona for every imported character")
    parser.add_argument("--conversation-method", default="Local LLM",
                        help='conversation method of the new characters (default: "Local LLM")')
    parser.add_argument("--update-avatars", action="store_true",
                        help="give characters that already exist the avatar from their card, "
                             "leaving everything else - their chats above all - untouched")
    parser.add_argument("--replace", action="store_true",
                        help="overwrite characters that already exist - this deletes their chats")
    parser.add_argument("--dry-run", action="store_true", help="only show what would be imported")
    args = parser.parse_args()

    persona_file = Path(args.persona).expanduser().resolve() if args.persona else None

    files = []
    for raw in args.paths:
        path = Path(raw).expanduser()
        if path.is_dir():
            files += sorted(p for p in path.glob("*.json") if p.resolve() != persona_file)
        else:
            files.append(path)

    characters = ConfigurationCharacters()
    settings = ConfigurationSettings()
    existing = characters.load_configuration().get("character_list", {})

    persona_name = args.persona_name
    cards, skipped = [], []
    for path in files:
        try:
            card = read_card(path)
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            if persona_file and path.resolve() == persona_file:
                continue
            print(f"  skipped {path.name}: {exc}")
            continue
        if card["name"] in existing and not args.replace:
            skipped.append(card)
            continue
        cards.append(card)

    if args.dry_run:
        for card in cards:
            print(f"  would import: {card['name']}")
        for card in skipped:
            note = "would update its avatar" if (card["avatar"] and args.update_avatars) else "would skip"
            print(f"  already there, {note}: {card['name']}")
        return 0

    if not args.dry_run:
        backup_configs()

    if args.lorebooks:
        import_lorebooks(args.lorebooks, settings, args.replace)

    if args.persona:
        for name, is_default in import_personas(persona_file, settings):
            print(f"  persona: {name}" + ("  (default)" if is_default else ""))
            if persona_name is None and is_default:
                persona_name = name

    for card in cards:
        avatar = cache_avatar(card["avatar"], card["name"]) if card["avatar"] else None
        characters.save_character_card(
            character_name=card["name"],
            character_title=card["title"],
            character_avatar=avatar,
            character_description=card["description"],
            character_personality=card["personality"],
            first_message=card["first_message"],
            scenario=card["scenario"],
            example_messages=card["example_messages"],
            alternate_greetings=card["alternate_greetings"],
            selected_persona=persona_name or "None",
            selected_system_prompt_preset="By default",
            selected_lorebook=None,
            elevenlabs_voice_id=None,
            voice_type=None,
            rvc_enabled=False,
            rvc_file=None,
            expression_images_folder=None,
            live2d_model_folder=None,
            vrm_model_file=None,
            conversation_method=args.conversation_method,
        )
        greetings = len(card["alternate_greetings"])
        print(f"  imported: {card['name']}" + (f"  (+{greetings} alternative greetings)" if greetings else ""))

    updated = 0
    if args.update_avatars and skipped:
        config = characters.load_configuration()
        for card in skipped:
            if not card["avatar"]:
                continue
            config["character_list"][card["name"]]["character_avatar"] = cache_avatar(card["avatar"], card["name"])
            updated += 1
        if updated:
            characters.save_configuration_edit(config)

    for card in skipped:
        note = "avatar updated" if (args.update_avatars and card["avatar"]) else "kept unchanged"
        print(f"  already there, {note}: {card['name']}")

    scenes_added = 0
    if args.scenes:
        scenes_added = import_scenes(
            args.scenes, args.replace,
            set(characters.load_configuration().get("character_list", {})),
            set(settings.get_user_data("lorebooks") or {}),
        )

    summary = f"{len(cards)} character(s) imported"
    if scenes_added:
        summary += f", {scenes_added} scene(s) imported"
    if updated:
        summary += f", {updated} avatar(s) updated"
    print(f"\n{summary}. Start the app to see them in the character list.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
