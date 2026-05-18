# Codex MD to Office Skill

Convert Markdown files into Office-style deliverables from Codex with Pandoc.

This repository packages a Codex-ready `md-to-office` skill for turning Markdown notes, reports, README files, outlines, and drafts into DOCX, PPTX, PDF, HTML, LaTeX, EPUB, ODT, or RTF files. The primary path is Markdown to Word (`.docx`), with optional table-of-contents and reference-template support.

## What It Does

- Converts one or more `.md` files to `.docx`, `.pptx`, `.pdf`, and other Pandoc-supported document formats.
- Supports `--reference-doc` for Word and PowerPoint templates.
- Validates generated DOCX/PPTX files as Office ZIP packages.
- Provides a small local wrapper script so Codex can run conversions without shell interpolation.

## Install

From Codex, ask:

```text
Use $skill-installer to install https://github.com/amos689/codex-md-to-office-skill/tree/main/skills/md-to-office
```

Or run the installer directly:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo amos689/codex-md-to-office-skill \
  --path skills/md-to-office
```

After installation, restart Codex or open a new Codex conversation so the new skill list is refreshed.

## Usage

Ask Codex:

```text
Use $md-to-office.
Convert examples/sample.md to DOCX at output/sample.docx with a table of contents.
```

Or run the bundled script directly:

```bash
python3 skills/md-to-office/scripts/convert_markdown.py examples/sample.md \
  --output /tmp/sample.docx \
  --toc
```

Use a Word reference template:

```bash
python3 skills/md-to-office/scripts/convert_markdown.py report.md \
  --output report.docx \
  --reference-doc template.docx \
  --toc
```

Dry-run the Pandoc command:

```bash
python3 skills/md-to-office/scripts/convert_markdown.py report.md \
  --output report.docx \
  --dry-run
```

## Requirements

- Codex with skills support.
- `pandoc` available on `PATH`.

Install Pandoc:

```bash
# macOS
brew install pandoc

# Ubuntu/Debian
sudo apt-get install pandoc
```

PDF output may require additional Pandoc PDF dependencies such as LaTeX or another PDF engine. DOCX output does not require LaTeX.

## Validation

Run the smoke test from the repository root:

```bash
bash tests/smoke_test.sh
```

The smoke test converts `examples/sample.md` to a temporary DOCX and checks that Pandoc produced a valid Office package.

## Attribution

This Codex adaptation is based on the MIT-licensed `md-to-office` skill from `claude-office-skills/skills`, simplified and repackaged for Codex.

Original project: https://github.com/claude-office-skills/skills/tree/main/md-to-office

## License

MIT. See `LICENSE`.
