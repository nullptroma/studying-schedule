#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT="$(cd "$REPORT_DIR/.." && pwd)"
REPORT_TYP="${REPORT_TYP:-reports/primer/report.typ}"
if [[ -z "${OUT_PDF:-}" ]]; then
  typ_abs="$REPORT_TYP"
  if [[ "$typ_abs" != /* ]]; then
    typ_abs="$REPORT_DIR/$typ_abs"
  fi
  OUT_PDF="${typ_abs%.typ}.pdf"
fi

echo "== check_gost_dashes =="
python3 "$SCRIPT_DIR/check_gost_dashes.py"

echo "== typst compile =="
cd "$REPORT_DIR"
if [[ "${FRONT_PDF:-}" != "" ]]; then
  BODY="$REPORT_DIR/.report.body.pdf"
  typst compile --root "$ROOT" "$REPORT_TYP" "$BODY"
  source "$SCRIPT_DIR/merge_front_matter.sh"
  merge_front_into_report "$REPORT_DIR" "$BODY"
  rm -f "$BODY"
else
  typst compile --root "$ROOT" "$REPORT_TYP" "$OUT_PDF"
fi

echo "Done: $OUT_PDF"
