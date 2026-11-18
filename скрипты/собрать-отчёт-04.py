#!/usr/bin/env python3
"""Собирает отчёт 4 из заметки постановки и заметок uml/, выгружает PlantUML."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "отчёт-4.md"
UML = ROOT / "uml"
OUT = ROOT / "Report" / "reports" / "04-uml"
PUML = ROOT / "Report" / "puml"
REPORT = OUT / "report.typ"

SPECIAL = set("\\#$*_`<>@~[]")
PORTRAIT_MAX_H = "21cm"
LANDSCAPE_MAX_H = "14.8cm"
PAGE_MARGIN = "margin: (left: 30mm, right: 15mm, top: 20mm, bottom: 20mm), footer: pz_page_footer"


def finish(text: str) -> str:
    text = text.strip()
    if text.endswith((".", "!", "?")):
        return text
    return text + "."


def escape(text: str) -> str:
    text = text.replace("—", "–")
    text = "".join("\\" + ch if ch in SPECIAL else ch for ch in text)
    return text.replace("\\_", "\\_\u200b")


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


def split_subsections(body: str) -> tuple[str, list[tuple[str, str]]]:
    parts = re.split(r"\n(?=### )", "\n" + body.strip())
    preamble = ""
    sections: list[tuple[str, str]] = []
    for part in parts:
        part = part.strip("\n")
        if part.startswith("### "):
            title, _, rest = part.partition("\n")
            sections.append((title[4:].strip(), rest.strip()))
        else:
            preamble = part.strip()
    return preamble, sections


def load(path: Path) -> tuple[dict[str, str], str, dict[str, str], str]:
    if not path.is_file():
        raise SystemExit(f"нет заметки: {path.relative_to(ROOT)}")
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    title, rest = h1_and_rest(body)
    preamble, sections = split_sections(rest)
    return meta, title, dict(sections), preamble


def render_table(caption: str, raw_rows: list[str], columns: str | None) -> str:
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
        f"  {columns.strip() if columns else width},",
        "  table.header(" + ", ".join(f"[{inline(cell)}]" for cell in header) + "),",
    ]
    for row in body:
        if len(row) > width:
            raise SystemExit(f"в таблице «{caption}» лишние ячейки: {row}")
        padded = row + [""] * (width - len(row))
        lines.append("  " + ", ".join(f"[{inline(cell)}]" for cell in padded) + ",")
    lines.append(")")
    table = "\n".join(lines)
    if width >= 3:
        table = "#text(size: 11pt)[\n" + table + "\n]"
    return table


def md_blocks(markdown: str, fallback_caption: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    index = 0
    pending: str | None = None
    columns: str | None = None
    markers = ("- ", "|", "Подпись:", "Колонки:", "### ")
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
        if stripped.startswith("|"):
            rows: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                rows.append(lines[index].strip())
                index += 1
            out.append(render_table(pending or fallback_caption, rows, columns))
            out.append("")
            pending = None
            columns = None
            continue
        if stripped.startswith("- "):
            while index < len(lines) and lines[index].strip().startswith("- "):
                out.append("- " + inline(lines[index].strip()[2:].strip()))
                index += 1
            out.append("")
            continue
        if re.match(r"\d+\.\s", stripped):
            while index < len(lines) and re.match(r"\d+\.\s", lines[index].strip()):
                out.append("+ " + inline(re.sub(r"^\d+\.\s+", "", lines[index].strip())))
                index += 1
            out.append("")
            continue
        paragraph = [stripped]
        index += 1
        while index < len(lines):
            nxt = lines[index].strip()
            if not nxt or nxt.startswith(markers) or re.match(r"\d+\.\s", nxt):
                break
            paragraph.append(nxt)
            index += 1
        out.append(inline(" ".join(paragraph)))
        out.append("")
    return "\n".join(out).rstrip()


def wrap(body: str) -> str:
    header = ["// Собран скриптом скрипты/собрать-отчёт-04.py."]
    if "pz-table" in body:
        header.append('#import "../../includes/common.typ": pz-table')
    if "pz_page_footer" in body:
        header.append('#import "../../includes/pz-pagination.typ": pz_page_footer')
    if "pz-table" in body:
        header.extend([
            "",
            "#show table: set par(justify: false)",
            "#show table: set enum(indent: 0pt, body-indent: 0.4em)",
        ])
    return "\n".join(header) + "\n\n" + body.rstrip() + "\n"


def write(name: str, text: str) -> None:
    path = OUT / name
    path.write_text(text, encoding="utf-8")
    print(path.relative_to(ROOT))


def require(sections: dict[str, str], names: tuple[str, ...], where: str) -> None:
    for name in names:
        if name not in sections:
            raise SystemExit(f"{where}: нет секции «{name}»")


def extract_plantuml(body: str, where: str) -> str:
    match = re.search(r"```plantuml\n(.*?)```", body, re.S)
    if not match:
        raise SystemExit(f"{where}: нет блока plantuml")
    code = match.group(1).strip() + "\n"
    if not code.startswith("@startuml") or "@enduml" not in code:
        raise SystemExit(f"{where}: блок plantuml без @startuml/@enduml")
    return code


def prepare_puml(code: str) -> str:
    header = "@startuml\n!include _gost-theme.inc.puml\nskinparam dpi 144\nskinparam monochrome false\n"
    return header + code[len("@startuml\n") :]


def first_paragraph(text: str) -> str:
    return " ".join(text.strip().split("\n\n")[0].split())


# --- главы -----------------------------------------------------------------


def intro(brief: dict[str, str]) -> str:
    return wrap("\n".join([
        "#heading(numbering: none, outlined: true)[Введение]",
        "",
        md_blocks(brief["Цель"], "Цель"),
        "",
        "Для достижения цели выполнены следующие задачи:",
        "",
        md_blocks(brief["Этапы"], "Этапы"),
        "",
        "Модель строится на требованиях работы № 1 и моделях DFD, IDEF0 и IDEF1 работы № 2. "
        "Диаграммы выполнены в PlantUML: этот инструмент выбран по итогам работы № 3. "
        "Исходные тексты диаграмм приведены в приложении А.",
    ]))


def requirements_chapter(brief: dict[str, str], registry: tuple[str, dict[str, str]]) -> str:
    preamble, subsections = split_subsections(brief["Предметная область"])
    parts = ["= Предметная область и требования", ""]
    if preamble:
        parts.extend([md_blocks(preamble, "Предметная область"), ""])
    for title, body in subsections:
        parts.extend(["== " + inline(title), "", md_blocks(body, title), ""])
    reg_preamble, reg = registry
    parts.extend(["== Реестр требований", ""])
    if reg_preamble:
        parts.extend([md_blocks(reg_preamble, "Реестр требований"), ""])
    parts.extend([md_blocks(reg["Реестр"], "Реестр требований"), ""])
    parts.extend(["== Критерии приёмки", "", md_blocks(reg["Критерии приёмки"], "Критерии приёмки")])
    return wrap("\n".join(parts))


def uc_cell(text: str) -> str:
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if lines and all(re.match(r"\d+\.\s", line) for line in lines):
        items = ", ".join("[" + inline(re.sub(r"^\d+\.\s+", "", line)) + "]" for line in lines)
        return f"[#enum(tight: true, {items})]"
    if lines and all(line.startswith("- ") for line in lines):
        return "[" + " #linebreak() ".join(inline(line[2:]) for line in lines) + "]"
    return "[" + inline(" ".join(lines)) + "]"


UC_FIELDS = (
    ("Актёры", "Актёры"),
    ("Предусловия", "Предусловия"),
    ("Основной поток", "Основной поток"),
    ("Альтернативы", "Альтернативы и исключения"),
    ("Постусловия", "Постусловия"),
    ("Трассировка", "Трассировка"),
)


def use_cases_chapter(cases: list[tuple[str, dict[str, str]]]) -> str:
    parts = [
        "= Спецификации ключевых прецедентов",
        "",
        "Ключевые прецеденты выбраны по двум признакам: высокая ценность для пользователя и высокий "
        "архитектурный риск. Каждый описан по шаблону методических указаний: актёры, предусловия, "
        "основной поток, альтернативы и исключения, постусловия и трассировка на требования.",
        "",
    ]
    for title, sections in cases:
        require(sections, tuple(name for name, _ in UC_FIELDS), title)
        uc_id, _, name = title.partition(". ")
        rows = [f"  [{label}], {uc_cell(sections[key])}," for key, label in UC_FIELDS]
        parts.extend([
            "== " + inline(title),
            "",
            "#pz-table(",
            f"  [Спецификация прецедента {inline(uc_id)} «{inline(name)}»],",
            "  (38mm, 1fr),",
            "  table.header([Поле], [Содержание]),",
            *rows,
            ")",
            "",
        ])
    return wrap("\n".join(parts))


def figure(meta: dict[str, str]) -> str:
    landscape = meta.get("ориентация", "книжная") == "альбомная"
    max_h = LANDSCAPE_MAX_H if landscape else PORTRAIT_MAX_H
    block = "\n".join([
        "#figure(",
        *([] if landscape else ["  placement: auto,"]),
        f'  pz-fit-image("../../images/{meta["рисунок"]}.png", {max_h}),',
        f"  caption: [{inline(meta['подпись'])}],",
        f") <{meta['метка']}>",
    ])
    if not landscape:
        return block
    return "\n".join([
        f"#set page(flipped: true, {PAGE_MARGIN})",
        block,
        f"#set page(flipped: false, {PAGE_MARGIN})",
    ])


FIT_IMAGE = """#let pz-fit-image(path, max-height) = layout(size => {
  let wide = image(path, width: size.width)
  if measure(wide).height > max-height { image(path, height: max-height) } else { wide }
})"""


def diagrams_chapter(diagrams: list[tuple[dict[str, str], str, dict[str, str], str]]) -> str:
    parts = [
        FIT_IMAGE,
        "",
        "= Комплект UML-диаграмм",
        "",
        f"Комплект состоит из {len(diagrams)} диаграмм. Для каждой указаны назначение в проекте, "
        "покрытые требования, принятые допущения и рисунок. Имена актёров, классов, операций и "
        "статусов одинаковы на всех диаграммах; проверка согласованности приведена в разделе 4.",
        "",
    ]
    for meta, title, sections, preamble in diagrams:
        require(sections, ("Покрытие", "Допущения", "Диаграмма"), title)
        parts.extend([
            "== " + inline(title),
            "",
            md_blocks(preamble, title),
            "",
            "#strong[Покрытие требований:] " + inline(finish(first_paragraph(sections["Покрытие"]))),
            "",
            "#strong[Допущения и ограничения:] " + inline(" ".join(sections["Допущения"].split())),
            "",
            f"Диаграмма приведена на #ref(<{meta['метка']}>, supplement: [рисунке]).",
            "",
            figure(meta),
            "",
        ])
    return wrap("\n".join(parts))


def trace_chapter(preamble: str, sections: dict[str, str]) -> str:
    parts = ["= Трассировка и проверка модели", ""]
    if preamble:
        parts.extend([md_blocks(preamble, "Трассировка"), ""])
    for title, body in sections.items():
        parts.extend(["== " + inline(title), "", md_blocks(body, title), ""])
    return wrap("\n".join(parts))


def appendix(diagrams: list[tuple[dict[str, str], str, dict[str, str], str]], codes: list[str]) -> str:
    parts = [
        '#import "../../includes/common.typ": pz-appendix-title',
        "",
        "#pz-appendix-title[Исходные тексты диаграмм PlantUML]",
        "",
        "#show raw: set text(font: \"DejaVu Sans Mono\", size: 8pt)",
        "#set par(first-line-indent: 0pt)",
        "",
        "Каждый листинг – содержимое блока plantuml в заметке диаграммы. При сборке скрипт "
        "добавляет к нему тему оформления по ГОСТ и выгружает в каталог Report/puml.",
        "",
    ]
    for number, ((meta, title, _s, _p), code) in enumerate(zip(diagrams, codes), 1):
        literal = code.replace("\\", "\\\\").replace('"', '\\"')
        parts.extend([
            f"#block(breakable: false, below: 0.4em)[Листинг А.{number} – {inline(meta['подпись'])}]",
            f'#block(width: 100%, inset: 6pt, stroke: 0.5pt, breakable: true, raw(block: true, "{literal}"))',
            "",
        ])
    return wrap("\n".join(parts))


def splice_includes(names: list[str]) -> None:
    text = REPORT.read_text(encoding="utf-8")
    block = "// body:begin\n" + "".join(f'#include "{name}"\n' for name in names) + "// body:end"
    new, count = re.subn(r"// body:begin\n.*?// body:end", block, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit("в report.typ нет маркеров body:begin / body:end")
    if new != text:
        REPORT.write_text(new, encoding="utf-8")


def main() -> None:
    _meta, _title, brief, _ = load(BRIEF)
    require(brief, ("Цель", "Этапы", "Предметная область", "Вывод", "Источники"), BRIEF.name)

    _m, _t, registry, reg_preamble = load(UML / "реестр-требований.md")
    require(registry, ("Реестр", "Критерии приёмки"), "реестр-требований.md")

    cases = []
    for path in sorted(UML.glob("UC-*.md")):
        meta, title, sections, _p = load(path)
        if meta.get("тип") == "прецедент":
            cases.append((int(meta.get("порядок", "0")), title, sections))
    cases.sort(key=lambda item: item[0])
    if not cases:
        raise SystemExit("нет заметок прецедентов uml/UC-*.md")

    diagrams = []
    for path in sorted(UML.glob("*.md")):
        meta, title, sections, preamble = load(path)
        if meta.get("тип") != "диаграмма":
            continue
        for key in ("порядок", "рисунок", "подпись", "метка"):
            if not meta.get(key):
                raise SystemExit(f"{path.name}: нет поля «{key}»")
        diagrams.append((meta, title, sections, preamble))
    diagrams.sort(key=lambda item: int(item[0]["порядок"]))

    _m, _t, trace, trace_preamble = load(UML / "трассировка.md")

    OUT.mkdir(parents=True, exist_ok=True)
    PUML.mkdir(parents=True, exist_ok=True)

    codes = []
    for meta, title, sections, _p in diagrams:
        code = extract_plantuml(sections["Диаграмма"], title)
        codes.append(code)
        puml = PUML / f"{meta['рисунок']}.puml"
        puml.write_text(prepare_puml(code), encoding="utf-8")
        print(puml.relative_to(ROOT))

    write("введение.typ", intro(brief))
    write("требования.typ", requirements_chapter(brief, (reg_preamble, registry)))
    write("прецеденты.typ", use_cases_chapter([(title, s) for _o, title, s in cases]))
    write("диаграммы.typ", diagrams_chapter(diagrams))
    write("трассировка.typ", trace_chapter(trace_preamble, trace))
    write("заключение.typ", wrap("\n".join([
        "#heading(numbering: none, outlined: true)[Заключение]",
        "",
        md_blocks(brief["Вывод"], "Вывод"),
    ])))
    write("источники.typ", wrap("\n".join([
        "#heading(numbering: none, outlined: true)[Список использованных источников]",
        "",
        md_blocks(brief["Источники"], "Источники"),
    ])))
    write("приложение-а.typ", appendix(diagrams, codes))
    splice_includes(["требования.typ", "прецеденты.typ", "диаграммы.typ", "трассировка.typ"])
    print(f"прецедентов: {len(cases)}, диаграмм: {len(diagrams)}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        raise SystemExit(0)
