"""
Small compatibility patches for third-party packages in the app's venv.
Safe to run repeatedly; each patch is skipped when its package is missing
or already patched.

- fairseq 0.12.2 (needed by rvc-python): Python 3.11 rejects mutable dataclass
  defaults such as `common: CommonConfig = CommonConfig()`, and fairseq never
  released a fix. Rewrite them to `field(default_factory=...)` and teach
  hydra_init() about default_factory.
- pyworld: reads its own version via the deprecated pkg_resources API, which
  prints a UserWarning on every start. Use importlib.metadata instead.
- qwen_tts: print()s a banner when the optional flash-attn package is missing.
  There are no flash-attn wheels for this PyTorch version, and qwen_tts falls
  back to plain PyTorch attention anyway, so log it at debug level instead.

Usage: <venv python> tools/patch_venv.py
"""

import re
import sys
import importlib.util
from pathlib import Path


def package_root(name: str):
    spec = importlib.util.find_spec(name)
    if spec is None or not spec.submodule_search_locations:
        return None
    return Path(spec.submodule_search_locations[0])


def rewrite(path: Path, transform) -> bool:
    text = path.read_text(encoding="utf-8")
    new = transform(text)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


# --------------------------------------------------------------------- fairseq
FAIRSEQ_PATTERNS = [
    (re.compile(r"^(\s+\w+): (\w+Config) = \2\(\)\s*$", re.M), r"\1: \2 = field(default_factory=\2)"),
    (re.compile(r"field\(\s*default=(\w+Config)\(\)"), r"field(default_factory=\1"),
]
HYDRA_OLD = "v = FairseqConfig.__dataclass_fields__[k].default\n"
HYDRA_NEW = (
    "_f = FairseqConfig.__dataclass_fields__[k]\n"
    "        v = _f.default_factory() if callable(getattr(_f, \"default_factory\", None)) else _f.default\n"
)


def patch_fairseq() -> int:
    root = package_root("fairseq")
    if root is None:
        return 0

    def transform(text, path):
        new = text
        for pattern, replacement in FAIRSEQ_PATTERNS:
            new = pattern.sub(replacement, new)
        if path.name == "initialize.py" and path.parent.name == "dataclass":
            new = new.replace(HYDRA_OLD, HYDRA_NEW)
        if new != text and not re.search(r"^from dataclasses import .*\bfield\b", new, re.M):
            new = "from dataclasses import field\n" + new
        return new

    patched = 0
    for path in root.rglob("*.py"):
        if "examples" not in path.parts and rewrite(path, lambda t, p=path: transform(t, p)):
            patched += 1
    return patched


# --------------------------------------------------------------------- pyworld
PYWORLD_OLD = "import pkg_resources\n\n__version__ = pkg_resources.get_distribution('pyworld').version"
PYWORLD_NEW = "from importlib.metadata import version as _dist_version\n\n__version__ = _dist_version('pyworld')"


def patch_pyworld() -> int:
    root = package_root("pyworld")
    if root is None:
        return 0
    return int(rewrite(root / "__init__.py", lambda t: t.replace(PYWORLD_OLD, PYWORLD_NEW)))


# -------------------------------------------------------------------- qwen_tts
QWEN_BANNER = re.compile(
    r'print\("\\n\*+\\nWarning: flash-attn is not installed\. (.*?)\\n\*+\\n ?"\)'
)


def patch_qwen_tts() -> int:
    root = package_root("qwen_tts")
    if root is None:
        return 0
    patched = 0
    for path in root.rglob("*.py"):
        if "flash-attn is not installed" not in path.read_text(encoding="utf-8"):
            continue
        replacement = r'__import__("logging").getLogger(__name__).debug("flash-attn is not installed. \1")'
        if rewrite(path, lambda t: QWEN_BANNER.sub(replacement, t)):
            patched += 1
    return patched


def main() -> int:
    for name, patch in (("fairseq", patch_fairseq), ("pyworld", patch_pyworld), ("qwen_tts", patch_qwen_tts)):
        print(f"{name}: {patch()} file(s) patched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
