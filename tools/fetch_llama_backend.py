"""
Download the official llama.cpp Linux build for one backend into
app/utils/ai_clients/backend/<backend>/ - the same thing the in-app backend
updater does, usable from the installer or the command line.

Usage: <venv python> tools/fetch_llama_backend.py [vulkan|cpu|hip|sycl]
"""

import os
import sys
import asyncio
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

from app.utils.backend_updater import LlamaUpdater  # noqa: E402


def main() -> int:
    backend = (sys.argv[1] if len(sys.argv) > 1 else "vulkan").lower()
    updater = LlamaUpdater(ROOT / "app" / "utils" / "ai_clients" / "backend")

    result = {}
    updater.progress_signal.connect(lambda percent, text: print(f"\r   {text}", end="", flush=True))
    updater.finished_signal.connect(lambda ok, msg: result.update(ok=ok, msg=msg))

    release, err = updater.fetch_latest_release_blocking()
    if err or not release:
        print(f"Could not query llama.cpp releases: {err}")
        return 1

    urls = updater._match_assets(release.get("assets", []), backend)
    if not urls:
        print(f"No official Linux build of llama.cpp for backend '{backend}' "
              "(CUDA: use the Vulkan backend or a system llama-server).")
        return 1

    print(f"   llama.cpp {release['tag_name']}: {urls[0].rsplit('/', 1)[-1]}")
    asyncio.run(updater._download_and_install(urls, backend, release["tag_name"]))
    print()
    print(f"   {result.get('msg', 'No result reported.')}")
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
