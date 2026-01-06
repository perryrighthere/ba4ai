---
name: ba4ai-option-a-coach
description: End-to-end coach for the BUS13551 BA x AI final project in this repo (Option A: pre-call targeting / direct marketing classification using the UCI Bank Marketing dataset id=222). Use when drafting the 10-minute video slide deck, the 500-word executive summary, or when aligning project.ipynb with the rubric (business framing, leakage-safe technique application, provenance/reproducibility, interpretation, recommendations, references, and 1-line GenAI disclosure).
---

# BA x AI Option A Coach (Direct Marketing / Pre‑Call Targeting)

Follow this workflow to maximise marks against `BA x AI Presentation Brief 2025-26.md` while staying consistent with:
- `OptionA_DirectMarketing_Classification_ProjectPlan.md`
- `OptionA_DirectMarketing_TechnicalPlan.md`
- `project.ipynb`

If any of the above files are missing or out of sync, fix that first.

## Quick start (what to produce)

1. **Notebook outputs (reproducible):** make `project.ipynb` run end-to-end and generate slide-ready figures/tables.
2. **Slides for a 10-minute recording:** use `assets/slides-outline-template.md` as the structure.
3. **Executive summary (≤500 words):** use `assets/executive-summary-template.md`.
4. **Always include:** dataset provenance + references + **one-line GenAI disclosure**.

## Workflow (rubric-aligned)

### 1) Business challenge (marks: /20)

Deliver in one slide and one spoken paragraph:
- **Decision:** who to call next (rank + choose a cut-off) under a call capacity `K`.
- **Objective:** maximise expected net profit (or conversions if profit is unknown).
- **Levers:** `K`, threshold `t`, ranking policy, agent allocation.
- **Constraints:** limited agent time, compliance/do-not-call, customer experience risk.
- **Assumptions (explicit):**
  - Profit per success `P` and cost per call `C` (use ranges; keep consistent in profit analysis).
  - Decision rule: call if `P·p̂ − C > 0` ⇒ `p̂ ≥ C/P`.

Use `references/assignment-rubric.md` as your “must not forget” checklist.

### 2) Technique application (marks: /30)

Be explicit about “decision moment” validity:
- **Option A = pre-call targeting** → exclude leakage/post-call fields.
- Maintain a **single scikit-learn pipeline** (imputation + encoding + model) for reproducibility.
- Use a defensible **model ladder**:
  - Dummy baseline
  - Logistic regression (interpretability)
  - One tree-based model (nonlinear)
- Use a split strategy you can explain (fixed seed, stratification). Keep test set sacred.
- If you recommend thresholds/profit policies, **check calibration**; calibrate if needed.

Open `references/option-a-scope-and-leakage.md` before you train anything.

### 3) Interpretation + recommendations (marks: /30)

Translate model results into decisions:
- Show **PR curve + PR-AUC** (primary) and base rate.
- Show **precision@K / recall@K / lift@K** at realistic capacities (multiple K values).
- Show **profit uplift vs random targeting** under a small `(P, C)` scenario grid.
- Provide a clear policy recommendation:
  - capacity fixed → call top‑K
  - capacity flexible → call if `p̂ ≥ C/P` (validated by profit curves)

Then operationalise like a real analyst:
- scoring workflow into CRM + monitoring (conversion rate, drift, calibration drift)
- retraining cadence and governance
- limitations (dataset context, drift risk, Option A exclusions)

### 4) Presentation quality (marks: /20)

Keep it within 10 minutes:
- Aim for **8–10 slides** and a single storyline.
- Put references on each slide footnote or a final references slide.
- Include a 1-line GenAI disclosure early (title slide) and/or at the end.

Use `assets/slides-outline-template.md` to draft slide titles + “what to show” + speaker notes.

## Quality gates (high-score checks)

Use these as pass/fail gates before recording:
- **Business framing:** decision, objective, levers, constraints, assumptions are stated.
- **Provenance:** dataset source + DOI + licence + access date are included.
- **Leakage control:** `duration` is excluded from Option A model (and you explain why).
- **Reproducibility:** seeds + split + key hyperparameters + versions are reported.
- **Business translation:** lift@K and profit uplift are shown vs a random baseline.
- **Recommendations:** actionable, measurable, and consistent with assumptions.
- **References + GenAI disclosure:** present and correct.

## Use the bundled templates

- Slide outline template: `assets/slides-outline-template.md`
- Executive summary template: `assets/executive-summary-template.md`
- GenAI disclosure templates: `assets/genai-disclosure-lines.txt`

