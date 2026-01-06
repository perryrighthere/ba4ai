# Executive Summary (≤500 words) — Template

Write in an executive tone. Avoid methodological jargon unless it directly supports a decision.

## 1) Problem and decision

- Business context (1–2 sentences).
- Decision to be made (who to call; capacity constraint).
- Objective (profit / conversions) + key levers + key constraints.

## 2) Data and provenance

- Dataset name/source, DOI, licence, access date.
- Sample size, target definition, base rate (class imbalance).
- Option A scope note (pre-call; leakage-safe feature set).

## 3) Method (analytics technique)

- Why classification is fit-for-purpose.
- What models you trained (dummy, logistic, tree).
- Reproducibility summary (split strategy, seed, versions).
- Calibration note if you use thresholds/profit rules.

## 4) Results (business translation)

- Headline performance (PR-AUC + base rate).
- Lift/precision@K at realistic capacities (1–2 sentences with numbers).
- Expected/realised profit uplift vs random targeting under explicit `(P, C)` assumptions.

## 5) Recommendation and implementation

- Policy: top‑K and/or threshold rule (`t=C/P`).
- Operational steps (scoring → CRM → agent workflow; monitoring; retraining cadence).
- Limitations and risks (drift; dataset context; missing CRM signals).

## 6) GenAI disclosure (one line)

Add one line: tool(s) used + what for + you verified results.

