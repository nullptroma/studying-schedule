#!/usr/bin/env python3
"""Приводит fig_*.puml к оформлению под ГОСТ: !include темы, без title и локальных skinparam."""
from __future__ import annotations

import re
from pathlib import Path

PUML_DIR = Path(__file__).resolve().parents[1] / "puml"
INCLUDE_LINE = "!include _gost-theme.inc.puml\n"


def strip_title_and_skinparam(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("skinparam"):
            if "{" in stripped and "}" not in stripped:
                i += 1
                while i < len(lines) and "}" not in lines[i]:
                    i += 1
                if i < len(lines):
                    i += 1
            else:
                i += 1
            continue
        if stripped.startswith("title"):
            if stripped == "title":
                i += 1
                while i < len(lines) and lines[i].strip() != "end title":
                    i += 1
                if i < len(lines):
                    i += 1
                continue
            i += 1
            continue
        if stripped in ("BackgroundColor", "BorderColor", "FontColor") or stripped.endswith(
            ("#F8F8F8", "#333333", "#E8F4FF", "#FFFDE7", "#F9A825")
        ):
            i += 1
            continue
        if stripped == "}" and out and out[-1].strip().startswith("!include"):
            i += 1
            continue
        out.append(line)
        i += 1
    return "".join(out)


def normalize_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    text = strip_title_and_skinparam(text)
    if INCLUDE_LINE.strip() not in text:
        m = re.match(r"(@startuml\s+\S+\s*\n)", text)
        if m:
            text = text[: m.end()] + INCLUDE_LINE + text[m.end() :]
    text = re.sub(r"\n{3,}", "\n\n", text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed = 0
    for path in sorted(PUML_DIR.glob("fig_*.puml")):
        if normalize_file(path):
            changed += 1
            print(f"updated: {path.name}")
    print(f"Done. {changed} file(s) changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
