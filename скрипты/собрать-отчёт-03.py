#!/usr/bin/env python3
"""Собирает отчёт 3 из заметки постановки и карточек инструментов."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "отчёт-3.md"
TOOLS = ROOT / "инструменты"
OUT = ROOT / "Report" / "reports" / "03-case"
IMAGES = ROOT / "Report" / "images"
REPORT = OUT / "report.typ"

SPECIAL = set("\\#$*_`<>@~[]")
SKIP_SECTIONS = {"Служебное", "Сборка", "Состав"}
CONDITION_SECTIONS = ("Потребности", "Критерии", "Кандидаты", "Сценарий")


def finish(text: str) -> str:
    text = text.strip()
    if text.endswith((".", "!", "?")):
        return text
    return text + "."


def escape(text: str) -> str:
    text = text.replace("—", "–")
    return "".join("\\" + ch if ch in SPECIAL else ch for ch in text)


def break_urls(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return "/\u200b".join(match.group(0).split("/"))

    return re.sub(r"https?://\S+", repl, text)


def inline(text: str) -> str:
    text = break_urls(text)
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


def render_table(caption: str, raw_rows: list[str], columns: str | None, flipped: bool) -> str:
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
    col_arg = columns.strip() if columns else str(width)
    lines = [
        "#pz-table(",
        f"  [{inline(caption)}],",
        f"  {col_arg},",
        "  table.header(" + ", ".join(f"[{inline(cell)}]" for cell in header) + "),",
    ]
    for row in body:
        padded = row + [""] * (width - len(row))
        if len(padded) < width:
            raise SystemExit(f"в таблице «{caption}» не хватает ячеек")
        lines.append("  " + ", ".join(f"[{inline(cell)}]" for cell in padded[:width]) + ",")
    lines.append(")")
    table = "\n".join(lines)
    if width >= 5:
        table = "#text(size: 9pt)[\n" + table + "\n]"
    if not flipped:
        return table
    return "\n".join([
        "#set page(flipped: true, margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer)",
        table,
        "#set page(flipped: false, margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer)",
    ])


def render_image(src: Path, caption: str) -> str:
    if not src.is_file():
        raise SystemExit(f"нет рисунка: {src}")
    safe = re.sub(r"[^0-9A-Za-z._-]+", "-", src.stem).strip("-") or "image"
    dest_name = f"fig_03_{safe}{src.suffix.lower()}"
    IMAGES.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, IMAGES / dest_name)
    try:
        from PIL import Image
    except ImportError:
        tall = False
    else:
        with Image.open(src) as im:
            w, h = im.size
        tall = h > w * 1.15
    if tall:
        image = "\n".join([
            "  image(",
            f'    "../../images/{dest_name}",',
            "    width: 100%,",
            "    height: 18cm,",
            '    fit: "contain",',
            "  ),",
        ])
    else:
        image = "\n".join([
            "  image(",
            f'    "../../images/{dest_name}",',
            "    width: 92%,",
            '    fit: "contain",',
            "  ),",
        ])
    label = "fig-03-" + safe
    return "\n".join([
        "#figure(",
        image,
        f"  caption: [{inline(caption)}],",
        f") <{label}>",
    ])


def md_blocks(markdown: str, fallback_caption: str, note_dir: Path) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    index = 0
    pending: str | None = None
    columns: str | None = None
    flipped = False
    image_re = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue
        if stripped.startswith("Подпись:"):
            pending = stripped.split(":", 1)[1].strip()
            index += 1
            continue
        if stripped.startswith("Колонки:"):
            columns = stripped.split(":", 1)[1].strip()
            index += 1
            continue
        if stripped.startswith("Разворот:"):
            flipped = stripped.split(":", 1)[1].strip().lower() in {"да", "yes", "true", "1"}
            index += 1
            continue
        if stripped.startswith("### "):
            out.append("== " + inline(stripped[4:].strip()))
            out.append("")
            index += 1
            continue
        image = image_re.match(stripped)
        if image:
            caption = pending or image.group(1).strip() or fallback_caption
            src = (note_dir / image.group(2)).resolve()
            out.append(render_image(src, caption))
            out.append("")
            pending = None
            columns = None
            flipped = False
            index += 1
            continue
        if stripped.startswith("|"):
            rows: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(lines[index].strip())
                index += 1
            out.append(render_table(pending or fallback_caption, rows, columns, flipped))
            out.append("")
            pending = None
            columns = None
            flipped = False
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
            if not nxt or nxt.startswith(("- ", "|", "Подпись:", "Колонки:", "Разворот:", "### ", "![")):
                break
            paragraph.append(nxt)
            index += 1
        out.append(inline(" ".join(paragraph)))
        out.append("")
    return "\n".join(out).rstrip()


def wrap(body: str) -> str:
    header = ["// Собран скриптом скрипты/собрать-отчёт-03.py."]
    if "pz-table" in body:
        header.append('#import "../../includes/common.typ": pz-table')
    if "pz_page_footer" in body:
        header.append('#import "../../includes/pz-pagination.typ": pz_page_footer')
    return "\n".join(header) + "\n\n" + body.rstrip() + "\n"


def chapter(title: str, preamble: str, sections: list[tuple[str, str]], note_dir: Path, lead: list[str]) -> str:
    parts = ["= " + inline(title), ""]
    for line in lead:
        parts.extend([inline(line), ""])
    if preamble:
        parts.extend([md_blocks(preamble, title, note_dir), ""])
    for section_title, section_body in sections:
        if section_title in SKIP_SECTIONS or not section_body.strip():
            continue
        parts.extend([
            "== " + inline(section_title),
            "",
            md_blocks(section_body, section_title, note_dir),
            "",
        ])
    return wrap("\n".join(parts).rstrip())


def write(name: str, text: str) -> None:
    path = OUT / name
    path.write_text(text, encoding="utf-8")
    print(path.relative_to(ROOT))


def load_tools() -> list[tuple[dict[str, str], str, str, Path]]:
    notes = []
    for path in sorted(TOOLS.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if meta.get("тип") != "инструмент":
            continue
        for key in ("порядок", "файл"):
            if not meta.get(key):
                raise SystemExit(f"{path.name}: нет поля «{key}»")
        title, rest = h1_and_rest(body)
        notes.append((meta, title, rest, path))
    notes.sort(key=lambda item: int(item[0]["порядок"]))
    return notes


def splice_includes(names: list[str]) -> None:
    text = REPORT.read_text(encoding="utf-8")
    block = "// body:begin\n" + "".join(f'#include "{name}"\n' for name in names) + "// body:end"
    new, count = re.subn(r"// body:begin\n.*?// body:end", block, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit("в report.typ нет маркеров body:begin / body:end")
    if new != text:
        REPORT.write_text(new, encoding="utf-8")


def section_map(body: str) -> dict[str, str]:
    _preamble, sections = split_sections(body)
    return dict(sections)


def main() -> None:
    if not BRIEF.exists():
        raise SystemExit(f"нет постановки: {BRIEF}")
    _, brief_body = parse_frontmatter(BRIEF.read_text(encoding="utf-8"))
    _title, brief_rest = h1_and_rest(brief_body)
    brief = section_map(brief_rest)
    for name in ("Цель", "Этапы", "Вывод", "Источники", *CONDITION_SECTIONS, "Сопоставление"):
        if name not in brief:
            raise SystemExit(f"в постановке нет секции «{name}»")

    tools = load_tools()
    if len(tools) != 4:
        raise SystemExit(f"ожидались 4 инструмента, найдено {len(tools)}")

    OUT.mkdir(parents=True, exist_ok=True)

    write("введение.typ", wrap("\n".join([
        "#heading(numbering: none, outlined: true)[Введение]",
        "",
        md_blocks(brief["Цель"], "Цель", ROOT),
        "",
        "Этапы работы:",
        "",
        md_blocks(brief["Этапы"], "Этапы", ROOT),
    ])))

    condition_sections = [(name, brief[name]) for name in CONDITION_SECTIONS]
    write("условия.typ", chapter("Подготовка сравнения", "", condition_sections, ROOT, []))

    includes = ["условия.typ"]
    for meta, title, rest, path in tools:
        preamble, sections = split_sections(rest)
        lead = []
        if meta.get("класс"):
            lead.append(finish(f"Класс инструмента: {meta['класс']}"))
        write(meta["файл"], chapter(title, preamble, sections, path.parent, lead))
        includes.append(meta["файл"])

    write("сопоставление.typ", chapter(
        "Обобщение результатов",
        brief["Сопоставление"],
        [],
        ROOT,
        [],
    ))
    includes.append("сопоставление.typ")

    write("заключение.typ", wrap("\n".join([
        "#heading(numbering: none, outlined: true)[Заключение]",
        "",
        md_blocks(brief["Вывод"], "Вывод", ROOT),
    ])))
    write("источники.typ", wrap("\n".join([
        "#heading(numbering: none, outlined: true)[Список использованных источников]",
        "",
        md_blocks(brief["Источники"], "Источники", ROOT),
    ])))
    splice_includes(includes)
    print(f"инструментов: {len(tools)}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        raise SystemExit(0)
