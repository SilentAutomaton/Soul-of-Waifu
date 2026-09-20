#!/usr/bin/env python3
"""
Downloads and installs Live2D Cubism models for Soul of Waifu into assets/emotions/live2d/.

Usage:
    app/data/envs/sow/bin/python tools/fetch_live2d_models.py --all
    app/data/envs/sow/bin/python tools/fetch_live2d_models.py unitychan haru_greeter
    app/data/envs/sow/bin/python tools/fetch_live2d_models.py --list
"""

import argparse
import io
import json
import os
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE2D_DEST = ROOT / "assets" / "emotions" / "live2d"

MODELS = {
    "unitychan": {
        "name": "Unity-chan",
        "description": "Blonde twintails, ribbons, idol outfit (Ayu Ikue)",
        "type": "zip_runtime",
        "url": "https://cubism.live2d.com/sample-data/bin/unitychan/unitychan_ja.zip",
        "runtime_prefix": "runtime/",
        "model_file": "unitychan.model3.json",
    },
    "haru_greeter": {
        "name": "Haru (Greeter / Office)",
        "description": "Dark hair, corporate blazer/suit (Marina Wakatsuki)",
        "type": "zip_runtime",
        "url": "https://cubism.live2d.com/sample-data/bin/haru_greeter/haru_greeter_ja.zip",
        "runtime_prefix": "runtime/",
        "model_file": "haru_greeter_t05.model3.json",
    },
    "senko": {
        "name": "Senko",
        "description": "Cat/fox ears, tail, maid apron, playful (Cosmos)",
        "type": "github_raw",
        "base_url": "https://raw.githubusercontent.com/Eikanya/Live2d-model/master/Live2D/Senko_Normals/",
        "files": [
            "senko.model3.json",
            "senko_normal.moc3",
            "senko.physics3.json",
            "senko_normal.4096/texture_00.png",
            "motions/Idle.motion3.json",
            "motions/Anim_1.motion3.json",
            "motions/Singing.motion3.json",
            "motions/Sleeping.motion3.json",
        ],
        "model_file": "senko.model3.json",
    },
    "haru": {
        "name": "Haru (Casual / Sporty)",
        "description": "Sporty jacket/hoodie, active expressions (Hazel Williams)",
        "type": "zip_runtime",
        "url": "https://cubism.live2d.com/sample-data/bin/haru/haru_ja.zip",
        "runtime_prefix": "runtime/",
        "model_file": "haru.model3.json",
    },
    "tsumiki": {
        "name": "Tsumiki Harugasa",
        "description": "Traditional Japanese kimono & hairstyle (Hifumi Yamamoto)",
        "type": "zip_runtime",
        "url": "https://cubism.live2d.com/sample-data/bin/tsumiki/tsumiki_ja.zip",
        "runtime_prefix": "runtime/",
        "model_file": "tsumiki.model3.json",
    },
    "rice": {
        "name": "Rice Glassfield",
        "description": "Long silver/lilac hair, fantasy gown (Yue)",
        "type": "zip_runtime",
        "url": "https://cubism.live2d.com/sample-data/bin/rice/rice_en.zip",
        "runtime_prefix": "runtime/",
        "model_file": "rice_pro_t03.model3.json",
    },
    "mao_pro": {
        "name": "Niziiro Mao (Pro)",
        "description": "Colorful, blend shapes, cheerful expressions",
        "type": "zip_runtime",
        "url": "https://cubism.live2d.com/sample-data/bin/mao/mao_en.zip",
        "runtime_prefix": "runtime/",
        "model_file": "mao_pro.model3.json",
    },
    "shizuku": {
        "name": "Shizuku",
        "description": "Dark hair, school/casual style",
        "type": "zip_runtime",
        "url": "https://cubism.live2d.com/sample-data/bin/shizuku/shizuku_ja.zip",
        "runtime_prefix": "runtime/",
        "model_file": "shizuku.model3.json",
    },
}


def download_bytes(url: str, desc: str = "") -> bytes:
    print(f"   Downloading {desc or url}...")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Soul-of-Waifu/Live2D-Fetcher"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def install_zip_runtime(dest_dir: Path, url: str, runtime_prefix: str, force: bool) -> None:
    data = download_bytes(url, url.split("/")[-1])
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for member in z.infolist():
            if member.is_dir():
                continue
            name = member.filename
            if not name.startswith(runtime_prefix):
                continue
            rel_name = name[len(runtime_prefix):]
            if not rel_name:
                continue
            target = dest_dir / rel_name
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and not force:
                continue
            with z.open(member) as src_f, open(target, "wb") as dst_f:
                shutil.copyfileobj(src_f, dst_f)


def install_github_raw(dest_dir: Path, base_url: str, files: list, force: bool) -> None:
    for rel in files:
        target = dest_dir / rel
        if target.exists() and not force:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        file_url = base_url + rel
        content = download_bytes(file_url, rel)
        target.write_bytes(content)


def install_model(key: str, force: bool = False) -> bool:
    info = MODELS.get(key)
    if not info:
        print(f"Unknown model: {key}")
        return False

    dest = LIVE2D_DEST / key
    model_file = dest / info["model_file"]
    if model_file.is_file() and not force:
        print(f"✓ {key} ({info['name']}) is already installed.")
        return True

    print(f"-> Installing {key} ({info['name']})...")
    dest.mkdir(parents=True, exist_ok=True)

    try:
        if info["type"] == "zip_runtime":
            install_zip_runtime(dest, info["url"], info["runtime_prefix"], force)
        elif info["type"] == "github_raw":
            install_github_raw(dest, info["base_url"], info["files"], force)
        else:
            print(f"Unsupported model type: {info['type']}")
            return False

        if model_file.is_file():
            print(f"✓ Successfully installed {key} to {dest.relative_to(ROOT)}")
            return True
        else:
            print(f"! Error: Expected model file not found: {model_file}")
            return False
    except Exception as exc:
        print(f"! Failed to install {key}: {exc}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Live2D models for Soul of Waifu.")
    parser.add_argument("models", nargs="*", help="Model keys to install (e.g. unitychan, haru_greeter)")
    parser.add_argument("--all", action="store_true", help="Install all default preset models")
    parser.add_argument("--force", action="store_true", help="Re-download and overwrite existing files")
    parser.add_argument("--list", action="store_true", help="List available models and install status")
    args = parser.parse_args()

    if args.list:
        print("Available Live2D models:")
        for k, v in MODELS.items():
            dest = LIVE2D_DEST / k / v["model_file"]
            status = "[INSTALLED]" if dest.is_file() else "[NOT INSTALLED]"
            print(f"  {k:15} {status:16} - {v['name']}: {v['description']}")
        return 0

    to_install = []
    if args.all:
        to_install = ["unitychan", "haru_greeter", "senko", "haru", "tsumiki", "rice"]
    elif args.models:
        to_install = args.models
    else:
        parser.print_help()
        return 1

    LIVE2D_DEST.mkdir(parents=True, exist_ok=True)

    failed = 0
    for key in to_install:
        if not install_model(key, force=args.force):
            failed += 1

    print("\nDone.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
