#!/usr/bin/env python3
"""Convert Markdown to Office-style formats with Pandoc.

This wrapper keeps Codex conversions predictable:
- no shell interpolation
- explicit input/template validation
- automatic output-format inference
- basic DOCX/PPTX package validation after conversion
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


SUPPORTED_FORMATS = {"docx", "pptx", "pdf", "html", "tex", "epub", "odt", "rtf"}
ZIP_FORMAT_MARKERS = {
    "docx": "word/document.xml",
    "pptx": "ppt/presentation.xml",
}


def infer_format(output: Path | None, explicit: str | None) -> str:
    if explicit:
        fmt = explicit.lower().lstrip(".")
    elif output and output.suffix:
        fmt = output.suffix.lower().lstrip(".")
    else:
        fmt = "docx"
    if fmt not in SUPPORTED_FORMATS:
        raise SystemExit(
            f"Unsupported target format '{fmt}'. Supported: "
            + ", ".join(sorted(SUPPORTED_FORMATS))
        )
    return fmt


def parse_metadata(values: list[str]) -> list[str]:
    args: list[str] = []
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Metadata must use KEY=VALUE syntax: {value}")
        key, val = value.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"Metadata key is empty: {value}")
        args.extend(["--metadata", f"{key}={val}"])
    return args


def validate_office_package(path: Path, fmt: str) -> None:
    marker = ZIP_FORMAT_MARKERS.get(fmt)
    if not marker:
        return
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
    except zipfile.BadZipFile as exc:
        raise SystemExit(f"Generated {fmt.upper()} is not a valid ZIP package: {path}") from exc
    if "[Content_Types].xml" not in names or marker not in names:
        raise SystemExit(
            f"Generated {fmt.upper()} is missing required Office package parts: {path}"
        )


def default_output(inputs: list[Path], fmt: str) -> Path:
    if len(inputs) != 1:
        raise SystemExit("--output is required when converting multiple Markdown files")
    return inputs[0].with_suffix(f".{fmt}")


def build_command(args: argparse.Namespace) -> tuple[list[str], Path, str]:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("pandoc was not found on PATH. Install Pandoc before converting.")

    inputs = [Path(p).expanduser().resolve() for p in args.inputs]
    if not inputs:
        raise SystemExit("At least one Markdown input is required")
    for path in inputs:
        if not path.is_file():
            raise SystemExit(f"Input file not found: {path}")

    raw_output = Path(args.output).expanduser().resolve() if args.output else None
    fmt = infer_format(raw_output, args.to)
    output = raw_output or default_output(inputs, fmt)
    output.parent.mkdir(parents=True, exist_ok=True)

    cmd = [pandoc, *[str(path) for path in inputs], "-o", str(output)]

    if args.reference_doc:
        reference = Path(args.reference_doc).expanduser().resolve()
        if not reference.is_file():
            raise SystemExit(f"Reference document not found: {reference}")
        cmd.append(f"--reference-doc={reference}")

    if args.toc:
        cmd.append("--toc")
    if args.toc_depth is not None:
        cmd.append(f"--toc-depth={args.toc_depth}")
    if args.number_sections:
        cmd.append("--number-sections")

    cmd.extend(parse_metadata(args.metadata or []))

    resource_paths = [Path.cwd(), *[path.parent for path in inputs]]
    if args.resource_path:
        resource_paths.extend(Path(p).expanduser().resolve() for p in args.resource_path)
    deduped: list[str] = []
    seen: set[str] = set()
    for path in resource_paths:
        text = str(path)
        if text not in seen:
            seen.add(text)
            deduped.append(text)
    cmd.append(f"--resource-path={':'.join(deduped)}")

    return cmd, output, fmt


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Markdown with Pandoc")
    parser.add_argument("inputs", nargs="+", help="Markdown input file(s)")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("--to", choices=sorted(SUPPORTED_FORMATS), help="Target format")
    parser.add_argument("--reference-doc", help="DOCX/PPTX reference template")
    parser.add_argument("--toc", action="store_true", help="Include a table of contents")
    parser.add_argument("--toc-depth", type=int, help="Table-of-contents heading depth")
    parser.add_argument("--number-sections", action="store_true", help="Number headings")
    parser.add_argument(
        "--metadata",
        action="append",
        default=[],
        help="Document metadata as KEY=VALUE; repeatable",
    )
    parser.add_argument(
        "--resource-path",
        action="append",
        default=[],
        help="Additional resource path for images/includes; repeatable",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print command only")
    args = parser.parse_args()

    cmd, output, fmt = build_command(args)
    if args.dry_run:
        print(json.dumps({"command": cmd, "output": str(output), "format": fmt}, indent=2))
        return 0

    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, file=sys.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode

    if not output.is_file() or output.stat().st_size == 0:
        raise SystemExit(f"Pandoc completed but output is missing or empty: {output}")
    validate_office_package(output, fmt)
    print(json.dumps({"ok": True, "output": str(output), "format": fmt}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
