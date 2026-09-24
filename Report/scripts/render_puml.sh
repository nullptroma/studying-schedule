#!/usr/bin/env bash
# Render Report/puml/fig_*.puml → Report/images/fig_*.png (имя PNG = @startuml в файле).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PUML_DIR="$REPORT_DIR/puml"
IMG_DIR="$REPORT_DIR/images"
GOST_CFG="$PUML_DIR/plantuml-gost.cfg"

mkdir -p "$IMG_DIR"

if [[ -z "${JAVA_HOME:-}" ]]; then
  for j in /usr/lib/jvm/java-21-openjdk /usr/lib/jvm/java-17-openjdk; do
    if [[ -x "$j/bin/java" ]]; then
      export JAVA_HOME="$j"
      break
    fi
  done
fi
export PATH="${JAVA_HOME:+$JAVA_HOME/bin:}$PATH"

JAR="${PLANTUML_JAR:-/usr/share/java/plantuml/plantuml.jar}"
JAVA_BIN="${JAVA_HOME:+$JAVA_HOME/bin/}java"
if [[ ! -f "$JAR" ]]; then
  echo "plantuml.jar not found at $JAR" >&2
  exit 1
fi

if [[ -f "$GOST_CFG" ]]; then
  python3 "$SCRIPT_DIR/normalize_puml_gost.py" >/dev/null
fi

shopt -s nullglob
PUML_FILES=("$PUML_DIR"/fig_*.puml)
if ((${#PUML_FILES[@]} == 0)); then
  echo "No fig_*.puml in $PUML_DIR" >&2
  exit 1
fi

# Лимит растра PlantUML (по умолчанию 4096); fig_04_domain_class упирался в 8192.
export PLANTUML_LIMIT_SIZE="${PLANTUML_LIMIT_SIZE:-16384}"
"$JAVA_BIN" -Djava.awt.headless=true \
  -DPLANTUML_LIMIT_SIZE="$PLANTUML_LIMIT_SIZE" \
  -Xmx3g \
  -jar "$JAR" \
  -charset UTF-8 -tpng \
  ${GOST_CFG:+-config "$GOST_CFG"} \
  -o "$IMG_DIR" "${PUML_FILES[@]}"

# Лёгкое сжатие только свежесгенерированных PNG из .puml (скриншоты не трогаем).
PNGQUANT="${PNGQUANT:-pngquant}"
PUML_PNG_QUALITY="${PUML_PNG_QUALITY:-28-45}"
if command -v "$PNGQUANT" >/dev/null 2>&1; then
  for puml in "${PUML_FILES[@]}"; do
    base="$(basename "$puml" .puml)"
    png="$IMG_DIR/${base}.png"
    if [[ -f "$png" ]]; then
      tmp="${png}.pquant.tmp"
      # Сохраняем альфа-канал (прозрачный фон из plantuml-gost.cfg).
      "$PNGQUANT" --quality="$PUML_PNG_QUALITY" --force --output "$tmp" "$png"
      mv -f "$tmp" "$png"
    fi
  done
  echo "PNGquant ($PUML_PNG_QUALITY) applied to PlantUML outputs."
else
  echo "WARN: pngquant not found, PlantUML PNG left uncompressed" >&2
fi

echo "Done. $(ls -1 "$IMG_DIR"/fig_*.png 2>/dev/null | wc -l) PNG in images/ (dpi 72, transparent background, plantuml-gost.cfg)."
