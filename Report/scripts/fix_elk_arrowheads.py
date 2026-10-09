#!/usr/bin/env python3
"""Поворачивает наконечники стрелок ELK по направлению последнего отрезка.

PlantUML с ``!pragma layout elk`` проводит ломаную верно, но polygon
наконечника всегда смотрит вниз. Если последний отрезок приходит к цели
не снизу, наконечник разворачивается так, чтобы остриё указывало на цель.
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

TOKEN = re.compile(
    r'<line x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"[^>]*/>'
    r"|"
    r'<polygon points="([^"]+)" fill="#000"[^>]*/>'
)


def _points(raw: str) -> list[tuple[float, float]]:
    nums = [float(part) for part in raw.split(",")]
    return list(zip(nums[0::2], nums[1::2]))


def _format_points(points: list[tuple[float, float]]) -> str:
    return ",".join(f"{x:.3f},{y:.3f}" for x, y in points)


def _aim(points: list[tuple[float, float]], dx: float, dy: float) -> list[tuple[float, float]]:
    """Поворачивает наконечник, который сейчас смотрит вниз, в сторону (dx, dy)."""
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return points
    ux, uy = dx / length, dy / length
    # Уже смотрит вниз — точки не трогаем.
    if uy > 0.99 and abs(ux) < 0.05:
        return points
    tip_x, tip_y = points[0]
    aimed: list[tuple[float, float]] = []
    for x, y in points:
        ox, oy = x - tip_x, y - tip_y
        # Матрица переводит вектор (0, 1) в (ux, uy).
        aimed.append((tip_x + uy * ox + ux * oy, tip_y - ux * ox + uy * oy))
    return aimed


def fix_svg(svg: str) -> tuple[str, int]:
    last_line: tuple[float, float, float, float] | None = None
    turned = 0
    out: list[str] = []
    cursor = 0
    for match in TOKEN.finditer(svg):
        out.append(svg[cursor : match.start()])
        cursor = match.end()
        if match.group(1) is not None:
            last_line = tuple(float(match.group(i)) for i in range(1, 5))  # type: ignore[assignment]
            out.append(match.group(0))
            continue
        raw = match.group(5)
        points = _points(raw)
        replacement = match.group(0)
        if last_line is not None and len(points) == 5:
            x1, y1, x2, y2 = last_line
            tip_x, tip_y = points[0]
            if abs(tip_x - x2) < 0.2 and abs(tip_y - y2) < 0.2:
                aimed = _aim(points, x2 - x1, y2 - y1)
                if aimed != points:
                    turned += 1
                    replacement = replacement.replace(
                        f'points="{raw}"',
                        f'points="{_format_points(aimed)}"',
                        1,
                    )
        out.append(replacement)
        last_line = None
    out.append(svg[cursor:])
    return "".join(out), turned


def main() -> None:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} input.svg output.svg", file=sys.stderr)
        sys.exit(2)
    source = Path(sys.argv[1]).read_text(encoding="utf-8")
    fixed, turned = fix_svg(source)
    Path(sys.argv[2]).write_text(fixed, encoding="utf-8")
    print(f"arrowheads turned: {turned}")


if __name__ == "__main__":
    main()
