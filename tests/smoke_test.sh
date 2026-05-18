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
    document_xml = archive.read("word/document.xml").decode("utf-8")

required = {"[Content_Types].xml", "word/document.xml"}
missing = required - names
if missing:
    raise SystemExit(f"missing Office package parts: {sorted(missing)}")

if document_xml.count("<m:oMath") < 2:
    raise SystemExit("expected Markdown LaTeX math to convert to Word OMML equations")

print(f"smoke test ok: {path}")
PY

rm -f "${OUT}"
