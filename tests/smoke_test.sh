#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$(mktemp -t codex-md-to-office.XXXXXX).docx"

python3 "${ROOT}/skills/md-to-office/scripts/convert_markdown.py" \
  "${ROOT}/examples/sample.md" \
  --output "${OUT}" \
  --toc

python3 - "${OUT}" <<'PY'
import sys
import zipfile

path = sys.argv[1]
with zipfile.ZipFile(path) as archive:
    names = set(archive.namelist())

required = {"[Content_Types].xml", "word/document.xml"}
missing = required - names
if missing:
    raise SystemExit(f"missing Office package parts: {sorted(missing)}")

print(f"smoke test ok: {path}")
PY

rm -f "${OUT}"
