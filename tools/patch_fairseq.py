"""
Make fairseq 0.12.2 importable on Python 3.11+ (needed by rvc-python).

Python 3.11 rejects mutable dataclass defaults such as
`common: CommonConfig = CommonConfig()`, and fairseq never released a fix.
This rewrites them to `field(default_factory=...)` and teaches hydra_init()
about default_factory. Safe to run repeatedly.

Usage: <venv python> tools/patch_fairseq.py
"""

import re
import sys
import importlib.util
from pathlib import Path

PATTERNS = [
    (re.compile(r"^(\s+\w+): (\w+Config) = \2\(\)\s*$", re.M), r"\1: \2 = field(default_factory=\2)"),
    (re.compile(r"field\(\s*default=(\w+Config)\(\)"), r"field(default_factory=\1"),
]

HYDRA_OLD = "v = FairseqConfig.__dataclass_fields__[k].default\n"
HYDRA_NEW = (
    "_f = FairseqConfig.__dataclass_fields__[k]\n"
    "        v = _f.default_factory() if callable(getattr(_f, \"default_factory\", None)) else _f.default\n"
)


def main() -> int:
    spec = importlib.util.find_spec("fairseq")
    if spec is None or not spec.submodule_search_locations:
        print("fairseq is not installed - nothing to patch.")
        return 0
    root = Path(spec.submodule_search_locations[0])

    patched = 0
    for path in root.rglob("*.py"):
        if "examples" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        new = text
        for pattern, replacement in PATTERNS:
            new = pattern.sub(replacement, new)
        if path.name == "initialize.py" and path.parent.name == "dataclass":
            new = new.replace(HYDRA_OLD, HYDRA_NEW)
        if new != text:
            if not re.search(r"^from dataclasses import .*\bfield\b", new, re.M):
                new = "from dataclasses import field\n" + new
            path.write_text(new, encoding="utf-8")
            patched += 1
            print(f"patched {path.relative_to(root)}")

    print(f"fairseq: {patched} file(s) patched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
