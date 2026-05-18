---
name: md-to-office
description: Convert Markdown files or Markdown content into Office-style deliverables with Pandoc, especially DOCX Word documents, PPTX slides, PDFs, HTML, LaTeX, or EPUB. Use when Codex is asked to turn `.md` notes, reports, README files, outlines, academic drafts, or generated Markdown into `.docx`, `.pptx`, `.pdf`, or other publishable document formats, optionally using a Word or PowerPoint reference template.
---

# Markdown To Office

Use this skill to convert Markdown into office document formats with Pandoc. Prefer the bundled script for repeatable conversions and direct `pandoc` commands for quick one-offs.

This Codex adaptation is based on the MIT-licensed `md-to-office` skill from `claude-office-skills/skills`, simplified for Codex and focused on reliable local execution.

## Workflow

1. Confirm the source Markdown path or create a temporary `.md` file when the user provides inline Markdown.
2. Choose the target format from the output extension. Default to DOCX when the user only says "Word" or "Office document".
3. Use a reference template when the user provides one:
   - DOCX: `--reference-doc template.docx`
   - PPTX: `--reference-doc template.pptx`
4. Run the conversion with the bundled script.
5. Verify the output exists and, for DOCX/PPTX, that the generated file is a valid Office ZIP package.
6. For high-stakes layout work, use the installed Documents/DOCX workflow to render or inspect the resulting document visually.

## Primary Command

From the skill directory, run:

```bash
python3 scripts/convert_markdown.py input.md --output output.docx
```

Common options:

```bash
python3 scripts/convert_markdown.py input.md --output output.docx --toc --toc-depth 3
python3 scripts/convert_markdown.py input.md --output output.docx --reference-doc template.docx
python3 scripts/convert_markdown.py intro.md body.md refs.md --output report.docx --toc
python3 scripts/convert_markdown.py slides.md --output deck.pptx --reference-doc theme.pptx
python3 scripts/convert_markdown.py input.md --output output.pdf
```

If the user wants to see the underlying Pandoc command without writing a document:

```bash
python3 scripts/convert_markdown.py input.md --output output.docx --dry-run
```

## Markdown Guidance

- Use YAML frontmatter for title, author, date, abstract, and document metadata.
- Use `#`, `##`, and `###` consistently; Pandoc maps headings to Word styles.
- Use standard LaTeX math delimiters for editable Word equations:
  - Inline: `$E = mc^2$` or `\(E = mc^2\)`
  - Block: `$$ ... $$` or `\[ ... \]`
- Use normal Markdown tables for simple tables. Complex tables may need DOCX cleanup after conversion.
- Use relative image paths near the Markdown file. The script sets Pandoc's resource path to the input file directories.
- For slides, structure Markdown with `#` for sections and `##` for individual slides.

## Direct Pandoc Fallback

Use direct Pandoc when the bundled script is too restrictive:

```bash
pandoc input.md -o output.docx
pandoc --from markdown+tex_math_dollars+tex_math_single_backslash+tex_math_double_backslash input.md -o output.docx
pandoc input.md --toc --toc-depth=3 -o output.docx
pandoc input.md --reference-doc=template.docx -o output.docx
pandoc slides.md --reference-doc=template.pptx -o deck.pptx
```

## Quality Expectations

- Do not promise pixel-perfect Word layout from Markdown alone.
- For DOCX output, standard LaTeX math should become editable Word OMML equations. If formulas remain literal text, check that they are not inside code fences and that custom macros are expanded or defined in the document.
- Use a reference DOCX/PPTX template for branded typography, margins, heading styles, or slide themes.
- Check generated documents before delivery. At minimum, confirm file existence and basic package validity; render or visually inspect when layout matters.
- Mention missing dependencies clearly. This skill requires `pandoc` on `PATH`.
