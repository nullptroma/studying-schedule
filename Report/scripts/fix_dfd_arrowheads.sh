#!/usr/bin/env bash
# ELK рисует наконечник всегда вниз. Разворачиваем его по последнему отрезку.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PUML="$REPORT_DIR/puml/fig_02_dfd_0.puml"
IMG_DIR="$REPORT_DIR/images"
SVG="$IMG_DIR/fig_02_dfd_0.svg"
PNG="$IMG_DIR/fig_02_dfd_0.png"
FIXED="$IMG_DIR/fig_02_dfd_0.fixed.svg"

if [[ ! -f "$PUML" ]]; then
  echo "skip arrow fix: $PUML not found" >&2
  exit 0
fi

JAR="${PLANTUML_JAR:-/usr/share/java/plantuml/plantuml.jar}"
export PLANTUML_LIMIT_SIZE="${PLANTUML_LIMIT_SIZE:-16384}"
java -Djava.awt.headless=true \
  -DPLANTUML_LIMIT_SIZE="$PLANTUML_LIMIT_SIZE" \
  -Xmx2g \
  -jar "$JAR" \
  -charset UTF-8 -tsvg \
  -config "$REPORT_DIR/puml/plantuml-gost.cfg" \
  -o "$IMG_DIR" "$PUML"

python3 "$SCRIPT_DIR/fix_elk_arrowheads.py" "$SVG" "$FIXED"
rsvg-convert -o "$PNG" "$FIXED"

PNGQUANT="${PNGQUANT:-pngquant}"
PUML_PNG_QUALITY="${PUML_PNG_QUALITY:-70-90}"
if command -v "$PNGQUANT" >/dev/null 2>&1; then
  tmp="${PNG}.pquant.tmp"
  "$PNGQUANT" --quality="$PUML_PNG_QUALITY" --force --output "$tmp" "$PNG"
  mv -f "$tmp" "$PNG"
fi

rm -f "$SVG" "$FIXED"
echo "DFD arrowheads fixed: $PNG"
