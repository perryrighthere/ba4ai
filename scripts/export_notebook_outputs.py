#!/usr/bin/env python3

from __future__ import annotations

import argparse
import base64
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _slugify(text: str, max_len: int = 60) -> str:
    text = text.strip().lower()
    text = re.sub(r"^#+\s*", "", text)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    if not text:
        return "section"
    return text[:max_len]


def _ensure_list_str(x: Any) -> list[str]:
    if x is None:
        return []
    if isinstance(x, str):
        return [x]
    if isinstance(x, list) and all(isinstance(i, str) for i in x):
        return x
    raise TypeError(f"Expected str or list[str], got {type(x)}")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _mime_to_ext(mime: str) -> str:
    if mime.endswith("+json") or mime == "application/json" or "json" in mime:
        return "json"
    return {
        "text/plain": "txt",
        "text/html": "html",
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/svg+xml": "svg",
    }.get(mime, "bin")


@dataclass
class Section:
    index: int
    title: str
    slug: str
    dir: Path
    markdown_path: Path


def _cell_markdown_text(cell: dict[str, Any]) -> str:
    return "".join(_ensure_list_str(cell.get("source")))


def _cell_heading(cell_md: str) -> str:
    for line in cell_md.splitlines():
        if line.strip().startswith("#"):
            return line.strip()
    # fallback: first non-empty line
    for line in cell_md.splitlines():
        if line.strip():
            return line.strip()
    return "Section"


def _normalize_output_data(data: Any) -> str:
    if isinstance(data, str):
        return data
    if isinstance(data, list) and all(isinstance(i, str) for i in data):
        return "".join(data)
    # some outputs store JSON-like objects here (rare); serialize
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_notebook(ipynb_path: Path, out_dir: Path) -> None:
    nb = json.loads(ipynb_path.read_text(encoding="utf-8"))
    cells = nb.get("cells", [])

    root = out_dir
    sections_dir = root / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "notebook": str(ipynb_path),
        "exports_root": str(root),
        "sections": [],
        "code_cells_without_outputs": [],
    }

    current_section: Section | None = None
    section_counter = 0

    def start_section(cell_index: int, md_text: str) -> Section:
        nonlocal section_counter
        heading = _cell_heading(md_text)
        slug = _slugify(heading)
        name = f"{section_counter:02d}_{slug}"
        section_dir = sections_dir / name
        section_dir.mkdir(parents=True, exist_ok=True)
        md_path = section_dir / f"{name}.md"
        _write_text(md_path, md_text)
        sec = Section(index=section_counter, title=heading, slug=slug, dir=section_dir, markdown_path=md_path)
        manifest["sections"].append(
            {
                "section_index": section_counter,
                "cell_index": cell_index,
                "title": heading,
                "slug": slug,
                "dir": str(section_dir),
                "markdown": str(md_path),
                "outputs": [],
            }
        )
        section_counter += 1
        return sec

    for i, cell in enumerate(cells):
        ctype = cell.get("cell_type")

        if ctype == "markdown":
            md_text = _cell_markdown_text(cell)
            current_section = start_section(i, md_text)
            continue

        if ctype != "code":
            continue

        if current_section is None:
            # Notebook has code before any markdown.
            current_section = start_section(-1, "# Preamble\n")

        assert current_section is not None
        sec_entry = None
        # Find manifest section for current_section
        for s in reversed(manifest["sections"]):
            if s["section_index"] == current_section.index:
                sec_entry = s
                break
        if sec_entry is None:
            continue

        # Always export the code cell source for slide-building/debugging, even if it has no outputs.
        code_stub = "".join(_ensure_list_str(cell.get("source"))).strip()
        if code_stub:
            code_path = current_section.dir / f"cell{i:02d}_code.py"
            _write_text(code_path, code_stub + "\n")
            sec_entry["outputs"].append({"cell_index": i, "type": "code", "path": str(code_path)})

        outputs = cell.get("outputs", [])
        if not outputs:
            manifest["code_cells_without_outputs"].append(
                {
                    "cell_index": i,
                    "cell_id": cell.get("id"),
                }
            )
            continue

        out_count = 0
        for out in outputs:
            out_type = out.get("output_type")

            if out_type == "stream":
                text = _normalize_output_data(out.get("text", ""))
                p = current_section.dir / f"cell{i:02d}_out{out_count:02d}_stream.txt"
                _write_text(p, text)
                sec_entry["outputs"].append({"cell_index": i, "type": "stream", "path": str(p)})
                out_count += 1
                continue

            if out_type in {"execute_result", "display_data"}:
                data = out.get("data", {}) or {}
                # Prefer images, then html, then plain text, then everything else.
                for mime, payload in data.items():
                    if mime.startswith("image/"):
                        ext = _mime_to_ext(mime)
                        p = current_section.dir / f"cell{i:02d}_out{out_count:02d}.{ext}"
                        if mime == "image/svg+xml":
                            _write_text(p, _normalize_output_data(payload))
                        else:
                            b64 = _normalize_output_data(payload)
                            _write_bytes(p, base64.b64decode(b64))
                        sec_entry["outputs"].append({"cell_index": i, "type": mime, "path": str(p)})
                        out_count += 1

                for mime in ["text/html", "text/plain"]:
                    if mime in data:
                        ext = _mime_to_ext(mime)
                        p = current_section.dir / f"cell{i:02d}_out{out_count:02d}.{ext}"
                        _write_text(p, _normalize_output_data(data[mime]))
                        sec_entry["outputs"].append({"cell_index": i, "type": mime, "path": str(p)})
                        out_count += 1

                for mime, payload in data.items():
                    if mime in {"text/html", "text/plain"} or mime.startswith("image/"):
                        continue
                    ext = _mime_to_ext(mime)
                    safe_mime = re.sub(r"[^a-zA-Z0-9._-]+", "_", mime)
                    p = current_section.dir / f"cell{i:02d}_out{out_count:02d}_{safe_mime}.{ext}"
                    _write_text(p, _normalize_output_data(payload))
                    sec_entry["outputs"].append({"cell_index": i, "type": mime, "path": str(p)})
                    out_count += 1
                continue

            if out_type == "error":
                traceback = "\n".join(_ensure_list_str(out.get("traceback", [])))
                p = current_section.dir / f"cell{i:02d}_out{out_count:02d}_error.txt"
                _write_text(p, traceback)
                sec_entry["outputs"].append({"cell_index": i, "type": "error", "path": str(p)})
                out_count += 1
                continue

            # Unknown output type: dump JSON.
            p = current_section.dir / f"cell{i:02d}_out{out_count:02d}_raw.json"
            _write_text(p, json.dumps(out, ensure_ascii=False, indent=2))
            sec_entry["outputs"].append({"cell_index": i, "type": "raw", "path": str(p)})
            out_count += 1

    _write_text(root / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    _write_text(
        root / "README.md",
        "\n".join(
            [
                "# Notebook export",
                "",
                f"- Source: `{ipynb_path}`",
                "- Each folder under `sections/` corresponds to a markdown cell (and contains the outputs of subsequent code cells until the next markdown cell).",
                "- `manifest.json` maps cell indices to exported files.",
                "- If a code cell has no saved outputs in the notebook file, it will still be exported as `cellXX_code.py` but there will be no plots/tables to export.",
                "",
            ]
        )
        + "\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--notebook", default="project.ipynb")
    parser.add_argument("--out", default="outputs/project-ipynb")
    args = parser.parse_args()

    export_notebook(Path(args.notebook), Path(args.out))


if __name__ == "__main__":
    main()
