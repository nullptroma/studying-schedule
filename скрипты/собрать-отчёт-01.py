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


RED = "#FF0000"
QUESTION = "#00B0F0"
ANSWER = "#00A000"
FORMULATION = "#0000FF"

# Ширины колонок из сданного docx, twip. Первая колонка – номер требования.
ID_WIDTH = 1050
VERIFY_WIDTHS = (ID_WIDTH, 1780, 3340, 3340, 3340, 3340)
STEP1_WIDTHS = (ID_WIDTH, 1660, 3367, 2128, 3066, 4917)
STEP2_WIDTHS = (ID_WIDTH, 3536, 1639, 2775, 3921, 3267)
ACTOR_WIDTHS = (3707, 11431)

VERIFY_HEADERS = (
    "№",
    "Группа",
    "Исходное требование (красным – уточняемые фразы)",
    "Вопрос владельцу продукта",
    "Ответ владельца продукта (предлагаемый)",
    "Новая формулировка требования",
)
STEP_HEADERS = (
    "№",
    "Словосочетание вначале предложения",
    "Подлежащее",
    "Сказуемое",
    "Дополнение",
    "Словосочетание в конце предложения",
)
REQ_TAIL = re.compile(r"\s*[—–-]\s*(?:\[[^\]]+\]\([^)]+\)|REQ-\d+)\s*$")

LANDSCAPE = """#set page(
  flipped: true,
  margin: (left: 15mm, right: 15mm, top: 14mm, bottom: 14mm),
)"""


def paragraphs(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]


def plain_text(text: str) -> str:
    return " ".join(" ".join(part.split()) for part in paragraphs(text))


def quote_variants(phrase: str) -> list[str]:
    variants = [phrase]
    swapped = phrase.replace("„", "«").replace("“", "»")
    if swapped != phrase:
        variants.append(swapped)
    return variants


def highlight(sentence: str, phrases: list[str]) -> str:
    spans: list[tuple[int, int]] = []
    occupied = [False] * len(sentence)
    for phrase in sorted(phrases, key=len, reverse=True):
        found: tuple[int, int] | None = None
        for variant in quote_variants(phrase):
            start = 0
            while True:
                index = sentence.find(variant, start)
                if index < 0:
                    break
                end = index + len(variant)
                if not any(occupied[index:end]):
                    found = (index, end)
                    break
                start = index + 1
            if found:
                break
        if found:
            begin, end = found
            spans.append(found)
            for index in range(begin, end):
                occupied[index] = True
    spans.sort()
    parts: list[str] = []
    cursor = 0
    for begin, end in spans:
        if cursor < begin:
            parts.append(escape(sentence[cursor:begin]))
        parts.append(f'#text(fill: rgb("{RED}"))[{escape(sentence[begin:end])}]')
        cursor = end
    if cursor < len(sentence):
        parts.append(escape(sentence[cursor:]))
    return "".join(parts)


def colored(text: str, color: str, bold: bool = False) -> str:
    weight = ', weight: "bold"' if bold else ""
    return f'#text(fill: rgb("{color}"){weight})[{escape(text)}]'


def original_cell(section: str, path: Path) -> str:
    raw = callout(section, "удалить", path)
    phrases: list[str] = []
    sentences: list[str] = []
    for paragraph in paragraphs(raw):
        if paragraph.startswith("Неоднозначный фрагмент"):
            phrases.extend(left or right for left, right in re.findall(r"«([^»]+)»|„([^“]+)“", paragraph))
        else:
            sentences.append(" ".join(paragraph.split()))
    return highlight(" ".join(sentences), phrases)


def docx_table(
    widths: tuple[int, ...],
    fill: str,
    size_pt: int,
    headers: tuple[str, ...],
    rows: list[list[str]],
    center_first: bool = False,
) -> str:
    columns = ", ".join(f"{width}fr" for width in widths)
    header_cells = []
    for index, title in enumerate(headers):
        align = "center + horizon" if center_first and index == 0 else "left + top"
        header_cells.append(
            "table.cell(fill: rgb(\"#%s\"), align: %s)[#text(weight: \"bold\")[%s]]" % (fill, align, escape(title))
        )
    header = ",\n      ".join(header_cells)
    lines = [
        "#[",
        f"  #set text(size: {size_pt}pt)",
        "  #set par(justify: false, first-line-indent: (amount: 0pt, all: true), leading: 0.65em, spacing: 0.4em)",
        "  #table(",
        f"    columns: ({columns}),",
        "    stroke: 0.5pt,",
        "    inset: 4pt,",
        "    align: left + top,",
        "    table.header(",
        "      repeat: true,",
        f"      {header},",
        "    ),",
    ]
    width = len(headers)
    for row in rows:
        padded = row + [""] * (width - len(row))
        cells = []
        for index, body in enumerate(padded[:width]):
            align = "center + horizon" if center_first and index == 0 else "left + top"
            cells.append(f"table.cell(align: {align}, breakable: false)[{body}]")
        cells = ", ".join(cells)
        lines.append(f"    {cells},")
    lines.extend(["  )", "]"])
    return "\n".join(lines)


def step_rows(section: str, path: Path, req_id: str) -> list[list[str]]:
    rows = markdown_table(section, path)
    number = escape(req_id)
    return [[number, *[inline(cell) for cell in row]] for row in rows[1:]]


def action_items(markdown: str) -> list[str]:
    items = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        items.append(inline(REQ_TAIL.sub("", stripped[2:].strip())))
    return items


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


def require_parts(meta: dict[str, str], parts: dict[str, str], path: Path) -> None:
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


def group_label(meta: dict[str, str]) -> str:
    group = meta["группа"]
    return group[:1].upper() + group[1:]


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
        "Критерии ясности и проверяемости взяты по Вигерсу и Битти. Пятиколоночная таблица и переход к активному залогу следуют алгоритму Липко. Контекст формализации требований описан в препринте ИСП РАН.",
        "",
    ]))

    verify_rows: list[list[str]] = []
    step1_rows: list[list[str]] = []
    step2_rows: list[list[str]] = []
    for meta, parts, path in requirements:
        require_parts(meta, parts, path)
        req_id = meta["id"]
        verify_rows.append([
            escape(req_id),
            escape(group_label(meta)),
            original_cell(parts["Исходная формулировка"], path),
            colored(plain_text(callout(parts["Вопрос владельцу продукта"], "вопрос", path)), QUESTION),
            colored(plain_text(callout(parts["Ответ владельца продукта"], "ответ", path)), ANSWER),
            colored(plain_text(callout(parts["Новая формулировка"], "формулировка", path)), FORMULATION, bold=True),
        ])
        step1_rows.extend(step_rows(parts["Шаг 1"], path, req_id))
        step2_rows.extend(step_rows(parts["Шаг 2"], path, req_id))

    verification = [
        "// Собран скриптом скрипты/собрать-отчёт-01.py из заметок требований.",
        "// Таблицы повторяют сетку сданного docx: альбомный лист, TableGrid, цвета ячеек.",
        LANDSCAPE,
        "",
        "= Верификация исходных требований",
        "",
        "Цветовое кодирование совпадает со сданным отчётом. "
        + f'#text(fill: rgb("{RED}"))[Красным] выделены фрагменты, которые предлагается удалить или уточнить. '
        + f'#text(fill: rgb("{QUESTION}"))[Голубым] записаны вопросы владельцу продукта. '
        + f'#text(fill: rgb("{ANSWER}"))[Зелёным] записаны ответы, предложенные командой: владелец продукта их ещё не подтвердил. '
        + f'#text(fill: rgb("{FORMULATION}"), weight: "bold")[Синим полужирным] дана новая формулировка требования.',
        "",
        docx_table(VERIFY_WIDTHS, "D9EAF7", 7, VERIFY_HEADERS, verify_rows, center_first=True),
        "",
        "== Табличное представление требований, шаг 1",
        "",
        docx_table(STEP1_WIDTHS, "E2F0D9", 8, STEP_HEADERS, step1_rows, center_first=True),
        "",
        "== Табличное представление требований, шаг 2",
        "",
        docx_table(STEP2_WIDTHS, "FFF2CC", 8, STEP_HEADERS, step2_rows, center_first=True),
        "",
    ]
    write("верификация.typ", "\n".join(verification))

    actor_rows: list[list[str]] = []
    for meta, parts, path in actors:
        items = action_items(parts["Действия"])
        if not items:
            raise SystemExit(f"{path.name}: у «{meta.get('имя', '')}» нет действий")
        bullets = " \\\n".join(f"• {item}" for item in items)
        actor_rows.append([escape(meta.get("имя", path.stem)), bullets])

    actor_lines = [
        "// Собран скриптом скрипты/собрать-отчёт-01.py из заметок акторов.",
        LANDSCAPE,
        "",
        "= Лист акторов и их действия",
        "",
        "Рабочая точка – уникальное подлежащее после перевода требования в активный залог. Веб-сайт и система здесь обозначают саму проектируемую систему.",
        "",
        docx_table(ACTOR_WIDTHS, "E2F0D9", 9, ("Актер", "Действия"), actor_rows),
        "",
    ]
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
