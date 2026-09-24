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


def resolve_live2d(name_or_path: str, card_dir: Path) -> str | None:
    """Finds the Live2D model folder by name or path."""
    if not name_or_path:
        return None
    raw = str(name_or_path).strip()
    p = Path(raw).expanduser()
    if p.is_dir():
        return str(p.resolve())
    card_rel = card_dir / raw
    if card_rel.is_dir():
        return str(card_rel.resolve())
    builtin = ROOT / "assets" / "emotions" / "live2d" / raw
    if builtin.is_dir():
        return str(builtin.resolve())
    return None


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
    live2d = data.get("extensions", {}).get("sow_live2d")
    live2d_folder = resolve_live2d(live2d, path.parent) if live2d else None
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
        "live2d_folder": live2d_folder,
        "live2d_name": str(live2d).strip() if live2d else None,
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


def deploy_backgrounds(source_dirs: list[Path]) -> int:
    """Copies background images from any backgrounds/ subfolder into assets/backgrounds/."""
    dest_dir = ROOT / "assets" / "backgrounds"
    dest_dir.mkdir(parents=True, exist_ok=True)
    deployed = 0
    seen = set()
    for raw in source_dirs:
        p = raw.resolve()
        candidate = p if p.name == "backgrounds" and p.is_dir() else (p / "backgrounds" if p.is_dir() else p.parent / "backgrounds")
        if not candidate.is_dir():
            continue
        for src in candidate.glob("*"):
            if src.suffix.lower() in (".jpg", ".png", ".jpeg") and src.name not in seen:
                seen.add(src.name)
                dest = dest_dir / src.name
                if not dest.exists() or src.stat().st_mtime > dest.stat().st_mtime:
                    shutil.copy2(src, dest)
                    deployed += 1
    return deployed


def backup_configs() -> None:
    for rel in CONFIG_FILES:
        src = ROOT / rel
        if src.exists():
            shutil.copy2(src, src.with_suffix(src.suffix + ".bak"))
    # characters.json is only the index - the characters themselves live in shards
    shards = ROOT / "app" / "configuration" / "characters"
    if shards.is_dir():
        backup = shards.with_name("characters.bak")
        shutil.rmtree(backup, ignore_errors=True)
        shutil.copytree(shards, backup)


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


def import_scenes(paths, replace: bool, known_characters, known_lorebooks, update_scenes: bool = False,
                   scene_group: str = None) -> int:
    """Soul Stage stores its scenes in .soul_stage/scenes.json, keyed by a uuid."""
    data = {"scenes": {}, "scene_groups": {}}
    if SCENES_FILE.exists():
        data = json.loads(SCENES_FILE.read_text(encoding="utf-8")) or data
    data.setdefault("scenes", {})
    data.setdefault("scene_groups", {})

    by_title = {v.get("title"): k for k, v in data["scenes"].items()}
    now = datetime.datetime.now().isoformat()
    added = 0
    group_sids = []

    for path in json_files(paths):
        scene = json.loads(path.read_text(encoding="utf-8"))
        title = str(scene.get("title") or "").strip()
        if not title:
            print(f"  skipped {path.name}: the scene has no title")
            continue
        if title in by_title and not replace:
            if update_scenes:
                sid = by_title[title]
                existing_scene = data["scenes"][sid]
                chat_log = existing_scene.get("chat_log", [])
                created_at = existing_scene.get("created_at", now)
                last_played = existing_scene.get("last_played", "")
                existing_scene.update(scene)
                existing_scene["chat_log"] = chat_log
                existing_scene["created_at"] = created_at
                existing_scene["last_played"] = last_played
                bg_info = f", bg: {existing_scene.get('starting_bg')}" if existing_scene.get("starting_bg") else ""
                print(f"  updated scene: {title}  ({existing_scene.get('gm_tone', '?')}{bg_info})")
                added += 1
                group_sids.append(sid)
                continue
            print(f"  scene already there, kept: {title}")
            group_sids.append(by_title[title])
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
        group_sids.append(sid)

    if scene_group and group_sids:
        members = data["scene_groups"].setdefault(scene_group, [])
        for sid in group_sids:
            if sid not in members:
                members.append(sid)
        print(f"  scene folder: {scene_group}  ({len(members)} scene(s))")

    if added or (scene_group and group_sids):
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
    parser.add_argument("--scene-group", metavar="NAME",
                        help="add every scene from --scenes to this Scene Folder in the Soul Stage lobby "
                             "(creates it if it doesn't exist yet)")
    parser.add_argument("--persona", metavar="FILE", help="persona file to import as well")
    parser.add_argument("--persona-name", metavar="NAME",
                        help="preselect this persona for every imported character")
    parser.add_argument("--conversation-method", default="Local LLM",
                        help='conversation method of the new characters (default: "Local LLM")')
    parser.add_argument("--update-avatars", action="store_true",
                        help="give characters that already exist the avatar from their card, "
                             "leaving everything else - their chats above all - untouched")
    parser.add_argument("--update-live2d", action="store_true",
                        help="assign configured Live2D models to characters that already exist, "
                             "leaving everything else - their chats above all - untouched")
    parser.add_argument("--update-scenes", action="store_true",
                        help="update settings of existing scenes (such as starting_bg) without clearing chat logs")
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
            l2d = f" (Live2D: {card['live2d_name']})" if card.get("live2d_folder") else ""
            print(f"  would import: {card['name']}{l2d}")
        for card in skipped:
            actions = []
            if card["avatar"] and args.update_avatars:
                actions.append("update avatar")
            if card.get("live2d_folder") and args.update_live2d:
                actions.append(f"update Live2D: {card['live2d_name']}")
            note = f"would {', '.join(actions)}" if actions else "would skip"
            print(f"  already there, {note}: {card['name']}")
        return 0

    if not args.dry_run:
        backup_configs()

    search_dirs = [Path(p).expanduser() for p in args.paths] + [Path(s).expanduser() for s in args.scenes]
    deployed_bgs = deploy_backgrounds(search_dirs)
    if deployed_bgs:
        print(f"  deployed {deployed_bgs} background image(s) to assets/backgrounds/")

    if args.lorebooks:
        import_lorebooks(args.lorebooks, settings, args.replace)

    if args.persona:
        for name, is_default in import_personas(persona_file, settings):
            print(f"  persona: {name}" + ("  (default)" if is_default else ""))
            if persona_name is None and is_default:
                persona_name = name

    for card in cards:
        avatar = cache_avatar(card["avatar"], card["name"]) if card["avatar"] else None
        live2d_folder = card.get("live2d_folder")
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
            live2d_model_folder=live2d_folder,
            vrm_model_file=None,
            conversation_method=args.conversation_method,
        )
        if live2d_folder:
            config = characters.load_configuration()
            config["character_list"][card["name"]]["current_sow_system_mode"] = "Live2D Model"
            characters.save_configuration_edit(config)

        greetings = len(card["alternate_greetings"])
        l2d_info = f"  (Live2D: {card['live2d_name']})" if live2d_folder else ""
        print(f"  imported: {card['name']}" + (f"  (+{greetings} alternative greetings)" if greetings else "") + l2d_info)

    updated_avatars = 0
    if args.update_avatars and skipped:
        config = characters.load_configuration()
        for card in skipped:
            if not card["avatar"]:
                continue
            config["character_list"][card["name"]]["character_avatar"] = cache_avatar(card["avatar"], card["name"])
            updated_avatars += 1
        if updated_avatars:
            characters.save_configuration_edit(config)

    updated_live2d = 0
    if args.update_live2d and skipped:
        config = characters.load_configuration()
        for card in skipped:
            if not card.get("live2d_folder"):
                continue
            char_entry = config["character_list"].get(card["name"])
            if not char_entry:
                continue
            char_entry["live2d_model_folder"] = card["live2d_folder"]
            char_entry["current_sow_system_mode"] = "Live2D Model"
            updated_live2d += 1
        if updated_live2d:
            characters.save_configuration_edit(config)

    for card in skipped:
        actions = []
        if args.update_avatars and card["avatar"]:
            actions.append("avatar updated")
        if args.update_live2d and card.get("live2d_folder"):
            actions.append(f"Live2D set to {card['live2d_name']}")
        note = ", ".join(actions) if actions else "kept unchanged"
        print(f"  already there, {note}: {card['name']}")

    scenes_added = 0
    if args.scenes:
        scenes_added = import_scenes(
            args.scenes, args.replace,
            set(characters.load_configuration().get("character_list", {})),
            set(settings.get_user_data("lorebooks") or {}),
            update_scenes=args.update_scenes,
            scene_group=args.scene_group,
        )

    summary = f"{len(cards)} character(s) imported"
    if scenes_added:
        summary += f", {scenes_added} scene(s) imported"
    if updated_avatars:
        summary += f", {updated_avatars} avatar(s) updated"
    if updated_live2d:
        summary += f", {updated_live2d} Live2D model(s) updated"
    if deployed_bgs:
        summary += f", {deployed_bgs} background(s) deployed"
    print(f"\n{summary}. Start the app to see them in the character list.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
