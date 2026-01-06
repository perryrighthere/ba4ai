# BA x AI (BUS13551) — Option A Direct Marketing Project

This repo contains a complete workflow for the BA x AI final project (2025–26), focusing on **Option A: pre-call targeting** (direct marketing classification).

## Key files

- Assignment brief: `BA x AI Presentation Brief 2025-26.md`
- Project plan (business framing + rubric mapping): `OptionA_DirectMarketing_Classification_ProjectPlan.md`
- Technical plan (notebook steps + artefacts checklist): `OptionA_DirectMarketing_TechnicalPlan.md`
- Working notebook: `project.ipynb`

## Recommended workflow (high level)

1. Work through the steps in `project.ipynb` (aligned to the technical plan).
2. Make sure the notebook is saved with outputs (tables/plots stored inside the `.ipynb` file).
3. Export notebook outputs into `outputs/` for slide building.
4. Concatenate exported artefacts into section-wise `compiled.html` files you can use for slides.

## Scripts

### 1) Export notebook markdown + outputs to `outputs/`

Exports each markdown section and the subsequent code-cell outputs (tables/plots) into a folder structure that’s easy to reuse for slides.

Run:

```bash
python3 scripts/export_notebook_outputs.py --notebook project.ipynb --out outputs/project-ipynb
```

Outputs:

- `outputs/project-ipynb/manifest.json` (mapping from notebook cells → exported files)
- `outputs/project-ipynb/sections/<NN_section-title>/...` (markdown + exported artifacts)

Important:

- If a code cell has **no saved outputs** in `project.ipynb`, there’s nothing to export for that cell (the script will still export the code as `cellXX_code.py`).

### 2) Concatenate section outputs into `compiled.md` / `compiled.html` (and optional PDF)

Concatenates each section folder’s markdown + exported artifacts (HTML tables, PNG plots, etc.) into a single “section-wise” document.

Run (HTML is the main output):

```bash
python3 scripts/concat_exported_sections.py --sections outputs/project-ipynb/sections --html
```

Outputs:

- Per section: `outputs/project-ipynb/sections/*/compiled.md` and `outputs/project-ipynb/sections/*/compiled.html`
- Combined: `outputs/project-ipynb/sections/compiled_all.md` and `outputs/project-ipynb/sections/compiled_all.html`

Optional PDF conversion (HTML → PDF via headless Chrome):

```bash
python3 scripts/concat_exported_sections.py --sections outputs/project-ipynb/sections --html --pdf
```

Notes:

- This uses **Google Chrome headless**. If your environment blocks Chrome’s headless printing, you’ll see `[pdf skipped] ...` messages; the HTML outputs are still generated and can be printed to PDF manually.

## Codex skills (optional)

These are project-specific skills created to keep you aligned to the rubric and to compute decision-grade targeting metrics:

- Coach (rubric + deliverables): `skills/ba4ai-option-a-coach/SKILL.md`
- Targeting metrics helpers: `skills/ba4ai-targeting-metrics/SKILL.md`

Packaged skill files (zip-with-`.skill` extension):

- `dist/ba4ai-option-a-coach.skill`
- `dist/ba4ai-targeting-metrics.skill`

