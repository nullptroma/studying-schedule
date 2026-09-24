#!/usr/bin/env python3
"""Сжатие скриншотов в images/ (JPEG и PNG). PNG из PlantUML не трогает."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

JPEG_QUALITY = "28"
PNGQUANT_QUALITY = "25-40"


def size_kb(path: Path) -> float:
    return path.stat().st_size / 1024


def puml_stems(report: Path) -> set[str]:
    puml = report / "puml"
    if not puml.is_dir():
        return set()
    return {p.stem for p in puml.glob("*.puml")}


def is_screenshot(path: Path, skip_stems: set[str]) -> bool:
    if path.stem in skip_stems:
        return False
    return path.suffix.lower() in {".jpg", ".jpeg", ".png"}


def compress_jpeg(path: Path, magick: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    subprocess.run(
        [magick, str(path), "-strip", "-quality", JPEG_QUALITY, str(tmp)],
        check=True,
        capture_output=True,
    )
    tmp.replace(path)


def compress_png(path: Path, pngquant: str) -> bool:
    tmp = path.with_suffix(".pngquant.tmp.png")
    for quality in (PNGQUANT_QUALITY, "15-55", "10-80"):
        try:
            subprocess.run(
                [
                    pngquant,
                    f"--quality={quality}",
                    "--force",
                    "--output",
                    str(tmp),
                    str(path),
                ],
                check=True,
                capture_output=True,
            )
            tmp.replace(path)
            return True
        except subprocess.CalledProcessError:
            if tmp.exists():
                tmp.unlink()
    print(f"  WARN: pngquant skip {path.name}", file=sys.stderr)
    return False


def main() -> int:
    report = Path(__file__).resolve().parents[1]
    images = report / "images"
    if not images.is_dir():
        print("No images/ directory", file=sys.stderr)
        return 1
    magick = shutil.which("magick") or shutil.which("convert")
    pngquant = shutil.which("pngquant")
    if not magick:
        print("ERROR: ImageMagick (magick/convert) not found", file=sys.stderr)
        return 1
    if not pngquant:
        print("ERROR: pngquant not found", file=sys.stderr)
        return 1

    skip = puml_stems(report)
    targets = sorted(
        p for p in images.iterdir() if p.is_file() and is_screenshot(p, skip)
    )
    if not targets:
        print("No screenshots to compress")
        return 0

    total_before = 0.0
    total_after = 0.0
    for path in targets:
        before = size_kb(path)
        total_before += before
        if path.suffix.lower() in {".jpg", ".jpeg"}:
            compress_jpeg(path, magick)
        else:
            compress_png(path, pngquant)
        after = size_kb(path)
        total_after += after
        pct = (1 - after / before) * 100 if before else 0
        print(f"  {path.name}: {before:.0f} KiB → {after:.0f} KiB (−{pct:.0f}%)")

    saved = (1 - total_after / total_before) * 100 if total_before else 0
    print(
        f"OK: {len(targets)} screenshots, "
        f"{total_before:.0f} KiB → {total_after:.0f} KiB (−{saved:.0f}%)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
