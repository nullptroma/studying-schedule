#!/usr/bin/env bash
# Склеивает PDF титула и тело отчёта (qpdf; без полей Typst на бланке).
set -euo pipefail

merge_front_into_report() {
  local report_dir="$1"
  local body_pdf="$2"
  local front_pdf="${FRONT_PDF:-$report_dir/front-matter-export/front.pdf}"
  local out_pdf="${OUT_PDF:-$report_dir/report.pdf}"
  local front_pages="${FRONT_PAGES:-3}"

  if [[ ! -f "$front_pdf" ]]; then
    echo "error: нет PDF первых страниц: $front_pdf" >&2
    return 1
  fi
  if [[ ! -f "$body_pdf" ]]; then
    echo "error: нет тела отчёта: $body_pdf" >&2
    return 1
  fi
  if ! command -v qpdf >/dev/null; then
    echo "error: нужен qpdf (https://qpdf.sourceforge.io/)" >&2
    return 1
  fi

  if command -v pdfinfo >/dev/null; then
    local n
    n="$(pdfinfo "$front_pdf" 2>/dev/null | awk '/^Pages:/ {print $2}')"
    if [[ -n "$n" && "$n" != "$front_pages" ]]; then
      echo "warning: в $front_pdf страниц: $n (ожидалось $front_pages)" >&2
    fi
  fi

  echo "== merge: $(basename "$front_pdf") + body → $(basename "$out_pdf") =="
  qpdf --warning-exit-0 --empty \
    --pages "$front_pdf" "1-$front_pages" "$body_pdf" 1-z \
    -- "$out_pdf"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  REPORT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
  BODY="${2:-$REPORT_DIR/.report.body.pdf}"
  merge_front_into_report "$REPORT_DIR" "$BODY"
fi
