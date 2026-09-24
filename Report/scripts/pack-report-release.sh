#!/usr/bin/env bash
# Собирает zip набора для каталога Report/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${1:-${GITHUB_REF_NAME:-${GITEA_REF_NAME:-dev}}}"
VERSION="${VERSION#v}"
OUT_DIR="${2:-"$ROOT/dist"}"
ARCHIVE="$OUT_DIR/gost-typst-Report-v${VERSION}.zip"

mkdir -p "$OUT_DIR"
# Каталог сборки вне дерева: иначе tar/rsync читает свой же приёмник внутри ROOT.
STAGING="$(mktemp -d "${TMPDIR:-/tmp}/gost-typst-report.XXXXXX")"
trap 'rm -rf "$STAGING"' EXIT

tar -C "$ROOT" \
  --exclude='.git' \
  --exclude='.gitea' \
  --exclude='dist' \
  --exclude='*.pdf' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.DS_Store' \
  --exclude='listings/generated' \
  -cf - . | tar -C "$STAGING" -xf -

rm -f "$ARCHIVE"
if command -v zip >/dev/null 2>&1; then
  (cd "$STAGING" && zip -r -q "$ARCHIVE" .)
elif command -v python3 >/dev/null 2>&1; then
  python3 - "$STAGING" "$ARCHIVE" <<'PY'
import os
import sys
import zipfile

src, dest = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for root, _dirs, files in os.walk(src):
        for name in files:
            path = os.path.join(root, name)
            archive.write(path, os.path.relpath(path, src))
PY
else
  echo "error: нужен zip или python3" >&2
  exit 1
fi

echo "Wrote $ARCHIVE"
if command -v unzip >/dev/null 2>&1; then
  unzip -l "$ARCHIVE"
else
  python3 - "$ARCHIVE" <<'PY'
import sys
import zipfile

with zipfile.ZipFile(sys.argv[1]) as archive:
    for info in archive.infolist():
        print(f"{info.file_size:8}  {info.filename}")
PY
fi
