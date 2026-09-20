#!/usr/bin/env bash
# Builds llama.cpp with CUDA and puts llama-server into the app's backend folder.
#
# llama.cpp publishes no CUDA build for Linux - only CPU, Vulkan, ROCm and SYCL - so the
# CUDA option in the app has nothing to run unless you build it yourself. Vulkan is fast on
# NVIDIA cards too; this is for the last few percent.
#
# Usage: ./tools/build_llama_cuda.sh [TAG] [CUDA_ARCH]
#   TAG        llama.cpp tag to build (default: the version the bundled backend reports)
#   CUDA_ARCH  compute capability without the dot - 89 = Ada (RTX 40xx), 86 = Ampere
#              (RTX 30xx), 75 = Turing (RTX 20xx), 120 = Blackwell (RTX 50xx)
#
# Needs: git, cmake, ninja, a C++ compiler and the CUDA toolkit (nvcc).

set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")/.."
ROOT="$PWD"

DEST="$ROOT/app/utils/ai_clients/backend/cuda"
SRC="${LLAMA_CUDA_SRC:-$HOME/development/llama.cpp-cuda-build}"
VERSION_FILE="$ROOT/app/utils/ai_clients/backend/version.json"

TAG="${1:-}"
if [ -z "$TAG" ] && [ -f "$VERSION_FILE" ]; then
    TAG=$(python3 -c "import json,sys; d=json.load(open('$VERSION_FILE')); print(next(iter(d.values()), ''))" 2>/dev/null || true)
fi
TAG="${TAG:-master}"
ARCH="${2:-89}"

NVCC="${NVCC:-/opt/cuda/bin/nvcc}"
command -v "$NVCC" >/dev/null 2>&1 || NVCC=$(command -v nvcc || true)
if [ -z "$NVCC" ]; then
    echo "nvcc not found - install the CUDA toolkit (Arch: 'cuda')." >&2
    exit 1
fi

echo "llama.cpp $TAG, CUDA architecture sm_$ARCH, nvcc: $NVCC"

if [ ! -d "$SRC/.git" ]; then
    git clone --depth 1 --branch "$TAG" https://github.com/ggml-org/llama.cpp "$SRC"
else
    git -C "$SRC" fetch --depth 1 origin "$TAG" && git -C "$SRC" checkout -q FETCH_HEAD
fi

cmake -S "$SRC" -B "$SRC/build" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_CUDA=ON \
    -DCMAKE_CUDA_ARCHITECTURES="$ARCH" \
    -DCMAKE_CUDA_COMPILER="$NVCC" \
    -DLLAMA_CURL=OFF \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_EXAMPLES=OFF \
    -DBUILD_SHARED_LIBS=ON

cmake --build "$SRC/build" -j "$(nproc)" --target llama-server

mkdir -p "$DEST"
# -a keeps the soname symlinks (libggml.so.0 -> libggml.so.0.24.0); without them the
# binary only finds its libraries as long as the build directory still exists.
find "$SRC/build" \( -name 'llama-server' -o -name '*.so*' \) -exec cp -a {} "$DEST/" \;
chmod +x "$DEST/llama-server"

echo
echo "Done: $DEST/llama-server"
echo "Pick GPU -> CUDA in the app's LLM settings. The backend updater does not know about"
echo "this build, so run the script again after an update of the bundled backends."
