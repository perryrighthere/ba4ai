#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


SECTION_MD_RE = re.compile(r"^\d{2}_.+\.md$")
CELL_CODE_RE = re.compile(r"^cell(\d{2})_code\.py$")
CELL_OUT_RE = re.compile(r"^cell(\d{2})_out(\d{2})_?.*?\.(\w+)$")


@dataclass(frozen=True, order=True)
class FileKey:
    group: int  # 0=section md, 1=code, 2=outputs, 9=other
    cell: int
    out: int
    name: str


def _sort_key(p: Path) -> FileKey:
    name = p.name
    if SECTION_MD_RE.match(name):
        return FileKey(group=0, cell=-1, out=-1, name=name)
    m = CELL_CODE_RE.match(name)
    if m:
        return FileKey(group=1, cell=int(m.group(1)), out=-1, name=name)
    m = CELL_OUT_RE.match(name)
    if m:
        return FileKey(group=2, cell=int(m.group(1)), out=int(m.group(2)), name=name)
    return FileKey(group=9, cell=10**9, out=10**9, name=name)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _is_image(path: Path) -> bool:
    return path.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg"}


def _is_html(path: Path) -> bool:
    return path.suffix.lower() == ".html"


def _is_md(path: Path) -> bool:
    return path.suffix.lower() == ".md"


def _is_txt(path: Path) -> bool:
    return path.suffix.lower() == ".txt"


def _is_json(path: Path) -> bool:
    return path.suffix.lower() == ".json"


def _fence(lang: str, content: str) -> str:
    return f"```{lang}\n{content.rstrip()}\n```\n"


def concat_section(section_dir: Path, *, include_code: bool, include_json: bool) -> Path:
    files = sorted([p for p in section_dir.iterdir() if p.is_file()], key=_sort_key)

    section_md_files = [p for p in files if SECTION_MD_RE.match(p.name)]
    section_md_path = section_md_files[0] if section_md_files else None

    parts: list[str] = []

    if section_md_path:
        parts.append(_read_text(section_md_path).rstrip() + "\n")
    else:
        parts.append(f"# {section_dir.name}\n")

    for p in files:
        if section_md_path and p == section_md_path:
            continue
        if CELL_CODE_RE.match(p.name):
            if not include_code:
                continue
            parts.append(f"\n\n---\n\n### {p.name}\n\n")
            parts.append(_fence("python", _read_text(p)))
            continue

        if _is_image(p):
            parts.append(f"\n\n![]({p.name})\n")
            continue

        if _is_html(p):
            # Raw HTML tables render well in many Markdown/Pandoc pipelines.
            parts.append(f"\n\n<!-- {p.name} -->\n\n")
            parts.append(_read_text(p).rstrip() + "\n")
            continue

        if _is_txt(p):
            parts.append(f"\n\n---\n\n<!-- {p.name} -->\n\n")
            parts.append(_fence("", _read_text(p)))
            continue

        if _is_json(p):
            if not include_json:
                continue
            parts.append(f"\n\n---\n\n<!-- {p.name} -->\n\n")
            parts.append(_fence("json", _read_text(p)))
            continue

        if _is_md(p):
            # Any extra markdown file in the section dir.
            parts.append("\n\n" + _read_text(p).rstrip() + "\n")
            continue

        # Unknown file: link it.
        parts.append(f"\n\n- `{p.name}`\n")

    out_path = section_dir / "compiled.md"
    out_path.write_text("".join(parts), encoding="utf-8")
    return out_path


def render_html(md_path: Path, *, resource_path: Path | None = None) -> Path:
    if not shutil.which("pandoc"):
        raise RuntimeError("pandoc is not available on PATH")
    html_path = md_path.with_suffix(".html")
    cmd = [
        "pandoc",
        str(md_path),
        "-o",
        str(html_path),
        "--from",
        "markdown+raw_html",
        "--standalone",
    ]
    if resource_path:
        cmd += ["--resource-path", str(resource_path)]
    subprocess.run(cmd, check=True)
    return html_path


def _find_chrome(user_chrome: str | None) -> str | None:
    if user_chrome:
        p = Path(user_chrome)
        if p.exists():
            return str(p)
        if shutil.which(user_chrome):
            return str(shutil.which(user_chrome))
        return None

    candidates = [
        # macOS app bundle (common)
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        # PATH candidates
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chrome"),
    ]
    for c in candidates:
        if not c:
            continue
        if Path(c).exists():
            return str(c)
    return None


def _is_file_url(s: str) -> bool:
    try:
        return urlparse(s).scheme == "file"
    except Exception:
        return False


def render_pdf_from_html(html_path: Path, *, chrome: str | None) -> Path:
    chrome_bin = _find_chrome(chrome)
    if not chrome_bin:
        raise RuntimeError(
            "Google Chrome not found. Install Chrome or pass --chrome /path/to/Chrome to enable HTML->PDF."
        )

    pdf_path = html_path.with_suffix(".pdf")
    url = html_path.resolve().as_uri()
    if not _is_file_url(url):
        raise RuntimeError(f"Unexpected HTML URI: {url}")

    # Use an isolated profile dir near the HTML file to avoid touching global Chrome profile/Crashpad paths,
    # which can fail under sandboxed/locked-down environments.
    with tempfile.TemporaryDirectory(prefix="chrome-pdf-", dir=str(html_path.parent)) as prof:
        cmd = [
            chrome_bin,
            "--headless",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-sync",
            "--metrics-recording-only",
            "--mute-audio",
            "--no-first-run",
            "--no-default-browser-check",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-crash-reporter",
            "--disable-breakpad",
            "--disable-features=Crashpad",
            f"--user-data-dir={prof}",
            "--print-to-pdf-no-header",
            f"--print-to-pdf={pdf_path}",
            url,
        ]
        subprocess.run(cmd, check=True)
    return pdf_path


def _rewrite_resource_links(section_name: str, text: str, resource_names: set[str]) -> str:
    # Rewrite Markdown images: ![](file.png) -> ![](section/file.png) when file exists in that section.
    def repl_md(m: re.Match[str]) -> str:
        target = m.group(1)
        if "/" in target or "\\" in target:
            return m.group(0)
        if target not in resource_names:
            return m.group(0)
        return m.group(0).replace(f"]({target})", f"]({section_name}/{target})")

    text = re.sub(r"!\[[^\]]*\]\(([^)]+)\)", repl_md, text)

    # Rewrite simple HTML src/href attributes that point to local files.
    def repl_attr(m: re.Match[str]) -> str:
        attr = m.group(1)
        target = m.group(2)
        if "/" in target or "\\" in target or target.startswith("http"):
            return m.group(0)
        if target not in resource_names:
            return m.group(0)
        return f'{attr}="{section_name}/{target}"'

    text = re.sub(r'(src|href)=\"([^\"]+)\"', repl_attr, text)
    return text


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Concatenate exported notebook section artifacts into compiled markdown, render HTML via pandoc, "
            "and optionally convert HTML -> PDF using headless Google Chrome."
        )
    )
    parser.add_argument("--sections", default="outputs/project-ipynb/sections", help="Root sections directory")
    parser.add_argument("--include-code", action="store_true", help="Include exported code cells in compiled markdown")
    parser.add_argument("--include-json", action="store_true", help="Include exported JSON artifacts in markdown")
    parser.add_argument(
        "--html",
        action="store_true",
        help="Render compiled.html via pandoc",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Convert compiled.html -> compiled.pdf using headless Chrome (implies HTML render)",
    )
    parser.add_argument("--chrome", default=None, help="Chrome executable path (defaults to common macOS location)")
    args = parser.parse_args()

    sections_root = Path(args.sections)
    if not sections_root.exists():
        raise SystemExit(f"Sections directory not found: {sections_root}")

    section_dirs = sorted([p for p in sections_root.iterdir() if p.is_dir()])
    if not section_dirs:
        raise SystemExit(f"No section directories found under: {sections_root}")

    compiled: list[Path] = []
    pdf_ok = 0
    pdf_fail = 0
    for sd in section_dirs:
        md = concat_section(sd, include_code=args.include_code, include_json=args.include_json)
        compiled.append(md)
        html_path = None
        if args.html or args.pdf:
            html_path = render_html(md, resource_path=sd)
        if args.pdf and html_path:
            try:
                render_pdf_from_html(html_path, chrome=args.chrome)
                pdf_ok += 1
            except Exception as e:
                print(f"[pdf skipped] {html_path}: {e}")
                pdf_fail += 1

    combined_md = sections_root / "compiled_all.md"
    parts: list[str] = ["# Notebook exports (compiled)\n\n"]
    for md in compiled:
        title = md.parent.name
        parts.append(f"\n\n<div style=\"page-break-after: always;\"></div>\n\n## {title}\n\n")
        resources = {p.name for p in md.parent.iterdir() if p.is_file()}
        section_text = _rewrite_resource_links(md.parent.name, _read_text(md), resources)
        parts.append(section_text.rstrip() + "\n")
    combined_md.write_text("".join(parts), encoding="utf-8")

    combined_html = None
    if args.html or args.pdf:
        combined_html = render_html(combined_md, resource_path=sections_root)
    if args.pdf and combined_html:
        try:
            render_pdf_from_html(combined_html, chrome=args.chrome)
            pdf_ok += 1
        except Exception as e:
            print(f"[pdf skipped] {combined_html}: {e}")
            pdf_fail += 1

    print(f"Wrote {len(compiled)} per-section compiled markdown files (compiled.md).")
    print(f"Wrote combined markdown: {combined_md}")
    if args.html:
        print("HTML files were rendered via pandoc (compiled.html).")
    if args.pdf:
        print(f"PDF render results: ok={pdf_ok}, failed={pdf_fail} (HTML -> PDF via headless Chrome).")
    if not args.html and not args.pdf:
        print("Rendering skipped (use --html and/or --pdf).")


if __name__ == "__main__":
    main()
