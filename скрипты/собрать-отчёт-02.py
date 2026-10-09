#!/usr/bin/env python3
"""Собирает главы отчёта 2 из заметок моделей и выгружает PlantUML."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "отчёт-2.md"
MODELS = ROOT / "модели"
OUT = ROOT / "Report" / "reports" / "02-моделирование"
PUML = ROOT / "Report" / "puml"
REPORT = OUT / "report.typ"

SPECIAL = set("\\#$*_`<>@~[]")


def escape(text: str) -> str:
    text = text.replace("—", "–").replace("«", "«").replace("»", "»")
    return "".join("\\" + ch if ch in SPECIAL else ch for ch in text)


def inline(text: str) -> str:
    parts: list[str] = []
    pattern = re.compile(r"\[([^\[\]]+)\]\((?:<[^>]+>|[^)]+)\)|\*\*([^*]+)\*\*")
    pos = 0
    for match in pattern.finditer(text):
        parts.append(escape(text[pos : match.start()]))
        if match.group(1) is not None:
            parts.append(escape(match.group(1)))
        else:
            parts.append("#strong[" + escape(match.group(2)) + "]")
        pos = match.end()
    parts.append(escape(text[pos:]))
    return "".join(parts)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line[:1] in " \t-" or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"').strip("'")
    return meta, body


def h1_and_rest(body: str) -> tuple[str, str]:
    match = re.match(r"#\s+(.+)\n+", body)
    if not match:
        raise SystemExit("у заметки нет заголовка первого уровня")
    return match.group(1).strip(), body[match.end() :]


def split_sections(body: str) -> tuple[str, list[tuple[str, str]]]:
    parts = re.split(r"\n(?=## )", body.strip())
    preamble = ""
    sections: list[tuple[str, str]] = []
    for part in parts:
        if part.startswith("## "):
            title, _, rest = part.partition("\n")
            sections.append((title[3:].strip(), rest.strip()))
        else:
            preamble = part.strip()
    return preamble, sections


def extract_plantuml(body: str, path: Path) -> tuple[str, str]:
    match = re.search(r"```plantuml\n(.*?)```", body, re.S)
    if not match:
        raise SystemExit(f"{path.name}: нет блока plantuml")
    code = match.group(1).strip() + "\n"
    if "@startuml" not in code or "@enduml" not in code:
        raise SystemExit(f"{path.name}: блок plantuml без @startuml/@enduml")
    rest = body[: match.start()] + body[match.end() :]
    return code, rest


def prepare_puml(code: str) -> str:
    if not code.startswith("@startuml"):
        raise SystemExit("PlantUML должен начинаться с @startuml")
    header = "@startuml\n!include _gost-theme.inc.puml\nskinparam dpi 144\nskinparam monochrome false\n"
    if code.startswith("@startuml\n"):
        code = header + code[len("@startuml\n") :]
    else:
        code = code.replace("@startuml", header.rstrip("\n"), 1)
    code = re.sub(r"\n{3,}", "\n\n", code)
    return code


def md_blocks(markdown: str, fallback_caption: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    index = 0
    pending: str | None = None
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith("Подпись:"):
            pending = stripped.split(":", 1)[1].strip()
            index += 1
            continue
        if stripped.startswith("|"):
            rows: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(lines[index].strip())
                index += 1
            out.append(render_table(pending or fallback_caption, rows))
            out.append("")
            pending = None
            continue
        if stripped.startswith("- "):
            items: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                items.append(lines[index].strip()[2:].strip())
                index += 1
            out.extend("- " + inline(item) for item in items)
            out.append("")
            continue
        paragraph = [stripped]
        index += 1
        while index < len(lines):
            nxt = lines[index].strip()
            if not nxt or nxt.startswith(("- ", "|", "Подпись:")):
                break
            paragraph.append(nxt)
            index += 1
        out.append(inline(" ".join(paragraph)))
        out.append("")
    return "\n".join(out).rstrip()


def render_table(caption: str, raw_rows: list[str]) -> str:
    rows: list[list[str]] = []
    for raw in raw_rows:
        cells = [cell.strip() for cell in raw.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        raise SystemExit(f"пустая таблица «{caption}»")
    header, body = rows[0], rows[1:]
    width = len(header)
    lines = [
        "#pz-table(",
        f"  [{inline(caption)}],",
        f"  {width},",
        "  table.header(" + ", ".join(f"[{inline(cell)}]" for cell in header) + "),",
    ]
    for row in body:
        padded = row + [""] * (width - len(row))
        lines.append("  " + ", ".join(f"[{inline(cell)}]" for cell in padded[:width]) + ",")
    lines.append(")")
    return "\n".join(lines)


def figure_block(image: str, caption: str, label: str) -> str:
    return "\n".join([
        f"Диаграмма приведена на #ref(<{label}>, supplement: [рисунке]).",
        "",
        "#set page(flipped: true, margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer)",
        "#figure(",
        "  image(",
        f'    "../../images/{image}.png",',
        "    width: 100%,",
        "    height: 14.8cm,",
        '    fit: "contain",',
        "  ),",
        f"  caption: [{inline(caption)}],",
        f") <{label}>",
        "#set page(flipped: false, margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer)",
    ])


def chapter(title: str, preamble: str, sections: list[tuple[str, str]], meta: dict[str, str]) -> str:
    parts = [
        "// Собран скриптом скрипты/собрать-отчёт-02.py.",
        '#import "../../includes/common.typ": pz-table',
        '#import "../../includes/pz-pagination.typ": pz_page_footer',
        "",
        "= " + inline(title),
        "",
    ]
    if preamble:
        parts.extend([md_blocks(preamble, title), ""])
    diagram: tuple[str, str] | None = None
    for section_title, section_body in sections:
        if section_title == "Диаграмма":
            diagram = (section_title, section_body)
            continue
        parts.extend([
            "== " + inline(section_title),
            "",
            md_blocks(section_body, section_title),
            "",
        ])
    if diagram is None:
        raise SystemExit(f"{meta.get('рисунок', title)}: нет секции «Диаграмма»")
    _title, diagram_body = diagram
    prose = md_blocks(diagram_body, "Диаграмма")
    if prose:
        parts.extend([prose, ""])
    parts.append(figure_block(meta["рисунок"], meta["подпись"], meta["метка"]))
    return "\n".join(parts).rstrip() + "\n"


def load_models() -> list[tuple[dict[str, str], str, str]]:
    if not MODELS.is_dir():
        raise SystemExit(f"нет каталога {MODELS}")
    notes = []
    for path in sorted(MODELS.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if meta.get("тип") != "модель":
            continue
        for key in ("порядок", "рисунок", "подпись", "метка", "файл"):
            if not meta.get(key):
                raise SystemExit(f"{path.name}: нет поля «{key}»")
        title, rest = h1_and_rest(body)
        code, rest = extract_plantuml(rest, path)
        notes.append((meta, title, rest, code, path))
    notes.sort(key=lambda item: int(item[0]["порядок"]))
    return notes


def splice_includes(names: list[str]) -> None:
    text = REPORT.read_text(encoding="utf-8")
    block = "// models:begin\n" + "".join(f'#include "{name}"\n' for name in names) + "// models:end"
    new, count = re.subn(r"// models:begin\n.*?// models:end", block, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit("в report.typ нет маркеров models:begin / models:end")
    if new != text:
        REPORT.write_text(new, encoding="utf-8")


def write(name: str, text: str) -> None:
    path = OUT / name
    path.write_text(text, encoding="utf-8")
    print(path.relative_to(ROOT))


def main() -> None:
    if not BRIEF.exists():
        raise SystemExit(f"нет постановки: {BRIEF}")
    _, brief_body = parse_frontmatter(BRIEF.read_text(encoding="utf-8"))
    _title, brief_rest = h1_and_rest(brief_body)
    _preamble, brief_sections = split_sections(brief_rest)
    brief = dict(brief_sections)
    for name in ("Цель", "Этапы", "Вывод"):
        if name not in brief:
            raise SystemExit(f"в постановке нет секции «{name}»")

    models = load_models()
    if not models:
        raise SystemExit("нет заметок моделей")

    OUT.mkdir(parents=True, exist_ok=True)
    PUML.mkdir(parents=True, exist_ok=True)

    write("введение.typ", "\n".join([
        "// Собран скриптом скрипты/собрать-отчёт-02.py из заметки постановки.",
        "#heading(numbering: none, outlined: true)[Введение]",
        "",
        md_blocks(brief["Цель"], "Цель"),
        "",
        "Для достижения цели выполнены следующие задачи:",
        "",
        md_blocks(brief["Этапы"], "Этапы"),
        "",
    ]) + "\n")

    includes: list[str] = []
    for meta, title, rest, code, path in models:
        puml_path = PUML / f"{meta['рисунок']}.puml"
        puml_path.write_text(prepare_puml(code), encoding="utf-8")
        print(puml_path.relative_to(ROOT))
        preamble, sections = split_sections(rest)
        write(meta["файл"], chapter(title, preamble, sections, meta))
        includes.append(meta["файл"])

    write("заключение.typ", "\n".join([
        "// Собран скриптом скрипты/собрать-отчёт-02.py из заметки постановки.",
        "#heading(numbering: none, outlined: true)[Заключение]",
        "",
        md_blocks(brief["Вывод"], "Вывод"),
        "",
    ]) + "\n")
    splice_includes(includes)
    print(f"моделей: {len(models)}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        raise SystemExit(0)
