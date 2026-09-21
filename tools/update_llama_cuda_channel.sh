#!/usr/bin/env bash
# Keeps the self-built CUDA llama.cpp backend on llama.cpp's pre-release channel.
#
# llama.cpp ships no Linux CUDA binaries and publishes no separate "stable" releases -
# every GitHub release (tag b<N>) is marked prerelease. Tracking the latest one *is*
# tracking the only channel that exists. The bundled Vulkan/CPU/HIP/SYCL backends keep
# using the app's own manual updater (Options -> LLM -> Update Backend) unchanged.
#
# Run standalone, or install the systemd user timer below for unattended updates:
#   systemctl --user enable --now llama-cuda-update.timer
#
# Usage: ./tools/update_llama_cuda_channel.sh [CUDA_ARCH]

set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."
ROOT="$PWD"

VERSION_FILE="$ROOT/app/utils/ai_clients/backend/version.json"
ARCH="${1:-89}"
API_URL="https://api.github.com/repos/ggml-org/llama.cpp/releases?per_page=5"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

current_tag=""
if [ -f "$VERSION_FILE" ]; then
    current_tag=$(python3 -c "import json; print(json.load(open('$VERSION_FILE')).get('cuda',''))" 2>/dev/null || true)
fi

latest_tag=$(curl -fsSL "$API_URL" | python3 -c "
import json, sys
data = json.load(sys.stdin)
tag = next((r['tag_name'] for r in data if str(r.get('tag_name','')).lower().startswith('b')), '')
print(tag)
")

if [ -z "$latest_tag" ]; then
    log "Could not determine the latest llama.cpp release tag - skipping."
    exit 1
fi

if [ "$latest_tag" = "$current_tag" ]; then
    log "llama.cpp CUDA backend already at latest pre-release ($current_tag) - nothing to do."
    exit 0
fi

log "Updating CUDA backend: $current_tag -> $latest_tag"
"$ROOT/tools/build_llama_cuda.sh" "$latest_tag" "$ARCH"
log "CUDA backend updated to $latest_tag."
