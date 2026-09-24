#!/usr/bin/env python3
"""В .typ отчёта нет длинного тире (нужно среднее)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIR_NAMES = {"listings", "extras", "puml", "scripts"}
SKIP_FILE_NAMES = {"Пример работы с Typst.typ"}
EM = "—"


def main() -> int:
    bad: list[str] = []
    for path in sorted(ROOT.rglob("*.typ")):
        if any(part in SKIP_DIR_NAMES for part in path.relative_to(ROOT).parts):
            continue
        if path.name in SKIP_FILE_NAMES:
            continue
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            if EM in line and "не длинное" not in line:
                bad.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()[:100]}")
    if bad:
        print("error: найдено длинное тире (нужно среднее):", file=sys.stderr)
        for line in bad[:40]:
            print(f"  {line}", file=sys.stderr)
        if len(bad) > 40:
            print(f"  ... и ещё {len(bad) - 40}", file=sys.stderr)
        return 1
    print("OK: длинное тире в .typ не найдено")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
