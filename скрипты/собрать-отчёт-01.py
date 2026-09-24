#!/usr/bin/env python3
"""Собирает главы отчёта 1 из заметок в каталог gost-typst."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ_DIR = ROOT / "требования"
ACTORS = ROOT / "акторы.md"
BRIEF = ROOT / "отчёт-1.md"
OUT = ROOT / "Report" / "reports" / "01-верификация"

SPECIAL = set("\\#$*_`<>@~[]")


def escape(text: str) -> str:
    text = text.replace("—", "–")
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


def sections(body: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for chunk in re.split(r"\n(?=## )", body.strip()):
        if not chunk.startswith("## "):
            continue
        title, _, rest = chunk.partition("\n")
        found[title[3:].strip()] = rest.strip()
    return found


def callout(section: str, kind: str, path: Path) -> str:
    lines: list[str] = []
    capture = False
    for line in section.splitlines():
        if line.startswith(f"> [!{kind}]") or line.startswith(f">[!{kind}]"):
            capture = True
            continue
        if not capture:
            continue
        if line.startswith("> "):
            lines.append(line[2:])
        elif line.strip() == ">":
            lines.append("")
        else:
            break
    text = "\n".join(lines).strip()
    if not text:
        raise SystemExit(f"{path.name}: пустой блок «{kind}»")
    return text


def markdown_table(section: str, path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        raise SystemExit(f"{path.name}: в секции нет таблицы")
    return rows


def blocks(markdown: str) -> str:
    output: list[str] = []
    paragraph: list[str] = []
    items: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            output.append(inline(" ".join(paragraph)))
            output.append("")
            paragraph.clear()

    def flush_items() -> None:
        if items:
            output.extend("- " + inline(item) for item in items)
            output.append("")
            items.clear()

    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_items()
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            items.append(stripped[2:].strip())
            continue
        flush_items()
        paragraph.append(stripped)
    flush_paragraph()
    flush_items()
    return "\n".join(output).strip()


def content_block(markdown: str) -> str:
    return "[\n" + blocks(markdown) + "\n]"


def table_block(section: str, caption: str, path: Path) -> str:
    rows = markdown_table(section, path)
    header, data = rows[0], rows[1:]
    width = len(header)
    columns = ", ".join(["1fr"] * width)
    lines = [
        "#block(breakable: false)[",
        "  #set text(size: 9pt)",
        "  #pz-table(",
        f"    [{inline(caption)}],",
        f"    ({columns}),",
        "    table.header(",
        "      " + ", ".join(f"[{inline(cell)}]" for cell in header) + ",",
        "    ),",
    ]
    for row in data:
        padded = row + [""] * (width - len(row))
        lines.append(
            "    "
            + ", ".join(
                f"table.cell(breakable: false)[{inline(cell)}]" for cell in padded[:width]
            )
            + ","
        )
    lines.extend(["  )", "]"])
    return "\n".join(lines)


def load_actors(path: Path) -> list[tuple[dict[str, str], dict[str, str], Path]]:
    chunks = re.split(r"\n(?=## )", path.read_text(encoding="utf-8"))
    actors = []
    for index, chunk in enumerate(chunks, start=1):
        if not chunk.startswith("## "):
            continue
        title, _, rest = chunk.partition("\n")
        lines: list[str] = []
        capture = False
        for line in rest.splitlines():
            if line.startswith("### Действия"):
                capture = True
                continue
            if capture and line.startswith("### "):
                break
            if capture:
                lines.append(line)
        actions = "\n".join(lines).strip()
        if not actions:
            raise SystemExit(f"{path.name}: у «{title[3:].strip()}» нет действий")
        actors.append(({"имя": title[3:].strip(), "порядок": str(index)}, {"Действия": actions}, path))
    return actors


def load_notes(directory: Path, expected_type: str) -> list[tuple[dict[str, str], dict[str, str], Path]]:
    notes = []
    for path in sorted(directory.glob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if meta.get("тип") != expected_type:
            continue
        notes.append((meta, sections(body), path))
    return notes


def requirement_block(meta: dict[str, str], parts: dict[str, str], path: Path) -> str:
    needed = (
        "Исходная формулировка",
        "Вопрос владельцу продукта",
        "Ответ владельца продукта",
        "Новая формулировка",
        "Шаг 1",
        "Шаг 2",
    )
    missing = [name for name in needed if name not in parts]
    if missing:
        raise SystemExit(f"{path.name}: нет секции «{missing[0]}»")
    heading = meta.get("заголовок") or path.stem
    return "\n".join([
        f"== {meta['id']}. {escape(heading)}",
        "",
        f"Группа: {inline(meta['группа'])}. Актор: {inline(meta['актор'])}.",
        "",
        "#подпись[Исходная формулировка]",
        "#удалить" + content_block(callout(parts["Исходная формулировка"], "удалить", path)),
        "",
        "#подпись[Вопрос владельцу продукта]",
        "#вопрос" + content_block(callout(parts["Вопрос владельцу продукта"], "вопрос", path)),
        "",
        "#подпись[Ответ владельца продукта, предложенный командой]",
        "#ответ" + content_block(callout(parts["Ответ владельца продукта"], "ответ", path)),
        "",
        "#подпись[Новая формулировка]",
        "#формулировка" + content_block(callout(parts["Новая формулировка"], "формулировка", path)),
        "",
        table_block(parts["Шаг 1"], f"{meta['id']}. Шаг 1, исходное предложение", path),
        "",
        table_block(parts["Шаг 2"], f"{meta['id']}. Шаг 2, активный залог", path),
        "",
    ])


def write(name: str, text: str) -> None:
    path = OUT / name
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(path.relative_to(ROOT))


def main() -> None:
    if not BRIEF.exists():
        raise SystemExit(f"Нет постановки: {BRIEF}")
    _, brief_body = parse_frontmatter(BRIEF.read_text(encoding="utf-8"))
    brief = sections(brief_body)
    for name in ("Цель", "Этапы", "Вывод"):
        if name not in brief:
            raise SystemExit(f"В постановке нет секции «{name}»")

    requirements = load_notes(REQ_DIR, "требование")
    actors = load_actors(ACTORS)
    if not requirements or not actors:
        raise SystemExit("Нет требований или акторов")
    requirements.sort(key=lambda item: item[0].get("id", ""))
    actors.sort(key=lambda item: int(item[0].get("порядок", "0")))

    OUT.mkdir(parents=True, exist_ok=True)

    write("введение.typ", "\n".join([
        "// Собран скриптом скрипты/собрать-отчёт-01.py из заметки постановки.",
        "#heading(numbering: none, outlined: true)[Введение]",
        "",
        blocks(brief["Цель"]),
        "",
        "Для достижения цели выполнены следующие задачи:",
        "",
        blocks(brief["Этапы"]),
        "",
        "Критерии ясности и проверяемости взяты по Вигерсу и Битти @wiegers2014. Пятиколоночная таблица и переход к активному залогу следуют алгоритму Липко @lipko2014. Контекст формализации требований описан в препринте ИСП РАН @kulyamin2006.",
        "",
    ]))

    verification = [
        "// Собран скриптом скрипты/собрать-отчёт-01.py из заметок требований.",
        '#import "../../includes/common.typ": pz-table',
        "",
        '#let удалить(body) = text(fill: rgb("#C00000"), body)',
        '#let вопрос(body) = text(fill: rgb("#2E75B6"), body)',
        '#let ответ(body) = text(fill: rgb("#548235"), body)',
        '#let формулировка(body) = text(fill: rgb("#1F4E79"), weight: "bold", body)',
        "#let подпись(название) = {",
        "  set par(first-line-indent: 0pt)",
        '  block(above: 0.8em, below: 0.2em, text(style: "italic", fill: luma(80), название))',
        "}",
        "",
        "= Верификация исходных требований",
        "",
        "Цветовое кодирование задания сохранено в тексте требований.",
        "",
        "#удалить[Красным выделены фрагменты, которые предлагается удалить или уточнить.]",
        "",
        "#вопрос[Голубым записаны вопросы владельцу продукта.]",
        "",
        "#ответ[Зелёным записаны ответы, предложенные командой. Владелец продукта их ещё не подтвердил.]",
        "",
        "#формулировка[Синим полужирным дана новая формулировка требования.]",
        "",
    ]
    for meta, parts, path in requirements:
        verification.append(requirement_block(meta, parts, path))
    write("верификация.typ", "\n".join(verification))

    actor_lines = [
        "// Собран скриптом скрипты/собрать-отчёт-01.py из заметок акторов.",
        "= Лист акторов и их действия",
        "",
        "Рабочая точка – уникальное подлежащее после перевода требования в активный залог. Веб-сайт и система здесь обозначают саму проектируемую систему.",
        "",
    ]
    for meta, parts, path in actors:
        if "Действия" not in parts:
            raise SystemExit(f"{path.name}: нет секции «Действия»")
        actor_lines.extend([
            f"== {escape(meta.get('имя', path.stem))}",
            "",
            blocks(parts["Действия"]),
            "",
        ])
    write("акторы.typ", "\n".join(actor_lines))

    write("заключение.typ", "\n".join([
        "// Собран скриптом скрипты/собрать-отчёт-01.py из заметки постановки.",
        "#heading(numbering: none, outlined: true)[Заключение]",
        "",
        blocks(brief["Вывод"]),
        "",
    ]))

    print(f"требований: {len(requirements)}, акторов: {len(actors)}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        raise SystemExit(0)
