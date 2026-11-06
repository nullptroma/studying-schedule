#!/usr/bin/env python3
"""Приводит диаграмму прецедентов Gaphor к составу PlantUML."""

from __future__ import annotations

import sys
from pathlib import Path

from gaphor.core.modeling import ElementFactory
from gaphor.diagram.export import save_png
from gaphor.diagram.general.simpleitem import Box
from gaphor.diagram.presentation import connect
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.storage import storage
from gaphor.UML.classes.association import AssociationItem
from gaphor.UML.usecases.actor import ActorItem
from gaphor.UML.usecases.extend import ExtendItem
from gaphor.UML.usecases.include import IncludeItem
from gaphor.UML.usecases.usecase import UseCaseItem
import gaphor.UML as UML


SOURCE = Path("/home/nullptr/Desktop/3 компаниец/UML.gaphor")

USE_CASES = [
    "Управлять учебными группами",
    "Управлять аудиториями",
    "Сформировать расписание",
    "Оптимизировать расписание",
    "Опубликовать расписание",
    "Скоректировать расписание",
    "Указать доступность преподавателя",
    "Запросить корректировку",
    "Посмотреть расписание",
]
RIGHT = {
    "Проверить ограничения": 2.45,
    "Минимизировать окна": 3.65,
}

ADMIN = [
    "Управлять учебными группами",
    "Управлять аудиториями",
    "Сформировать расписание",
    "Оптимизировать расписание",
    "Опубликовать расписание",
    "Скоректировать расписание",
]
TEACHER = [
    "Указать доступность преподавателя",
    "Запросить корректировку",
    "Посмотреть расписание",
]
STUDENT = ["Посмотреть расписание"]

INCLUDES = [
    ("Сформировать расписание", "Проверить ограничения"),
    ("Оптимизировать расписание", "Проверить ограничения"),
    ("Оптимизировать расписание", "Минимизировать окна"),
]
# Стрелка как в PlantUML: от «Посмотреть расписание» к «Запросить корректировку».
EXTEND = ("Посмотреть расписание", "Запросить корректировку", "При обнаружении ошибок")

UC_W = 250
UC_H = 64
ROW = 112
TOP = 48
LEFT_X = 280
RIGHT_X = 760
ACTOR_X = 36


def place(item, x: float, y: float, w: float | None = None, h: float | None = None) -> None:
    item.matrix.set(1, 0, 0, 1, x, y)
    if w is not None:
        item.width = w
    if h is not None:
        item.height = h


def load(path: Path) -> ElementFactory:
    factory = ElementFactory()
    language = ModelingLanguageService()
    with path.open(encoding="utf-8") as handle:
        storage.load(handle, factory, language)
    return factory


def save(path: Path, factory: ElementFactory) -> None:
    with path.open("w", encoding="utf-8") as handle:
        storage.save(handle, factory)


def diagram_of(factory: ElementFactory):
    diagrams = list(factory.select(UML.UseCaseDiagram))
    if len(diagrams) != 1:
        raise SystemExit(f"ожидалась одна диаграмма прецедентов, найдено {len(diagrams)}")
    return diagrams[0]


def actors_of(factory: ElementFactory) -> dict[str, UML.Actor]:
    found = {actor.name: actor for actor in factory.select(UML.Actor)}
    expected = {"Администратор", "Преподаватель", "Студент"}
    if set(found) != expected:
        raise SystemExit(f"актёры в файле: {sorted(found)}")
    return found


def clear_draft(factory: ElementFactory, diagram) -> None:
    for kind in (UML.Include, UML.Extend, UML.Association):
        for element in list(factory.select(kind)):
            element.unlink()
    for element in list(factory.select(UML.UseCase)):
        element.unlink()
    for item in list(diagram.ownedPresentation):
        if isinstance(item, (ActorItem, type(None))):
            continue
        if item.__class__.__name__ == "MetadataItem":
            continue
        if isinstance(item, ActorItem):
            continue
        item.unlink()


def presentation(subject, kind):
    items = [item for item in subject.presentation if isinstance(item, kind)]
    if len(items) != 1:
        raise SystemExit(f"у {subject.name!r} презентаций {kind.__name__}: {len(items)}")
    return items[0]


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE
    png = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    factory = load(SOURCE)
    diagram = diagram_of(factory)
    package = diagram.element if isinstance(diagram.element, UML.Package) else None
    if package is None:
        packages = list(factory.select(UML.Package))
        if len(packages) != 1:
            raise SystemExit("не найден пакет модели")
        package = packages[0]
    people = actors_of(factory)
    clear_draft(factory, diagram)

    column = {name: index for index, name in enumerate(USE_CASES)}
    column.update(RIGHT)
    # Рамка создаётся раньше эллипсов: в Gaphor раньше созданный элемент рисуется ниже.
    box = diagram.create(Box)
    place(
        box,
        LEFT_X - 36,
        TOP - 28,
        RIGHT_X + UC_W - LEFT_X + 72,
        (max(column.values()) + 1) * ROW + 36,
    )
    box.label = ""

    items: dict[str, UseCaseItem] = {}
    for name, index in column.items():
        subject = factory.create(UML.UseCase)
        subject.name = name
        subject.package = package
        item = diagram.create(UseCaseItem, subject=subject)
        x = RIGHT_X if name in RIGHT else LEFT_X
        place(item, x, TOP + index * ROW, UC_W, UC_H)
        items[name] = item

    def actor_y(names: list[str]) -> float:
        indexes = [column[name] for name in names]
        center = TOP + (min(indexes) + max(indexes)) / 2 * ROW + UC_H / 2
        return center - 30

    for item in diagram.ownedPresentation:
        if item.__class__.__name__ == "MetadataItem":
            place(item, LEFT_X, TOP + (max(column.values()) + 1) * ROW + 48)

    for name, linked in (
        ("Администратор", ADMIN),
        ("Преподаватель", TEACHER),
        ("Студент", STUDENT),
    ):
        actor_item = presentation(people[name], ActorItem)
        place(actor_item, ACTOR_X, actor_y(linked))

    def side_point(item, side: str) -> tuple[float, float]:
        x = float(item.matrix[4])
        y = float(item.matrix[5])
        if side == "right":
            return x + item.width, y + item.height / 2
        if side == "left":
            return x, y + item.height / 2
        if side == "top":
            return x + item.width / 2, y
        if side == "bottom":
            return x + item.width / 2, y + item.height
        raise SystemExit(f"неизвестная сторона: {side}")

    def relate(kind, tail, head, tail_side: str = "right", head_side: str = "left"):
        line = diagram.create(kind)
        line.tail.pos = side_point(tail, tail_side)
        line.head.pos = side_point(head, head_side)
        connect(line, line.tail, tail)
        connect(line, line.head, head)
        if line.subject is None:
            raise SystemExit(f"не связались {tail} -> {head}")
        return line

    for name in ADMIN:
        relate(AssociationItem, presentation(people["Администратор"], ActorItem), items[name])
    for name in TEACHER:
        relate(AssociationItem, presentation(people["Преподаватель"], ActorItem), items[name])
    for name in STUDENT:
        relate(AssociationItem, presentation(people["Студент"], ActorItem), items[name])
    for source, target in INCLUDES:
        relate(IncludeItem, items[source], items[target])
    extend = relate(ExtendItem, items[EXTEND[0]], items[EXTEND[1]], "top", "bottom")
    extend.subject.name = EXTEND[2]

    diagram.update(diagram.ownedPresentation)
    save(out, factory)

    check = load(out)
    names = sorted(uc.name for uc in check.select(UML.UseCase))
    expected = sorted([*USE_CASES, *RIGHT])
    if names != expected:
        raise SystemExit(f"состав прецедентов не сошёлся: {names}")
    includes = sorted(
        (inc.includingCase.name, inc.addition.name) for inc in check.select(UML.Include)
    )
    if includes != sorted(INCLUDES):
        raise SystemExit(f"include не сошлись: {includes}")
    extends = [
        (ext.extension.name, ext.extendedCase.name, ext.name)
        for ext in check.select(UML.Extend)
    ]
    if extends != [(EXTEND[0], EXTEND[1], EXTEND[2])]:
        raise SystemExit(f"extend не сошёлся: {extends}")

    def linked_to(actor_name: str) -> set[str]:
        actor = next(a for a in check.select(UML.Actor) if a.name == actor_name)
        names = set()
        for assoc in check.select(UML.Association):
            ends = [end.type for end in assoc.memberEnd if end.type]
            if actor in ends:
                other = next(end for end in ends if end is not actor)
                names.add(other.name)
        return names

    if linked_to("Администратор") != set(ADMIN):
        raise SystemExit(f"связи администратора: {linked_to('Администратор')}")
    if linked_to("Преподаватель") != set(TEACHER):
        raise SystemExit(f"связи преподавателя: {linked_to('Преподаватель')}")
    if linked_to("Студент") != set(STUDENT):
        raise SystemExit(f"связи студента: {linked_to('Студент')}")

    if png is not None:
        save_png(png, diagram_of(check))
    print(f"записано: {out}")
    if png:
        print(f"рисунок: {png}")


if __name__ == "__main__":
    main()
