# Option A Project Plan — Direct Marketing Offer Prioritisation (Pre‑Call Targeting)

This plan aligns with the marking scheme in `BA x AI Presentation Brief 2025-26.md`:
- **Business challenge** clarity (objectives, levers, constraints, assumptions) **/20**
- **Technique application** (justification, method, data/parameters, provenance, reproducibility) **/30**
- **Interpretation** (metrics + visuals + business translation + practical recommendations) **/30**
- **Presentation** (professional, referenced, AI disclosure, within 10 minutes) **/20**

Main storyline: **Option A — pre‑call targeting**: decide who to call *before* any call is made.

## 1) One‑sentence pitch (opening slide)

Build a pre‑call propensity model to rank customers by likelihood of subscribing to a term deposit, then recommend a call list (top‑K / threshold) that maximises expected campaign profit under limited calling capacity.

## 2) Business challenge framing (targets /20)

### 2.1 Context (make it “real”)
- A bank runs outbound phone campaigns for term deposits.
- Calls are capacity‑limited (agents/time) and costly; poor targeting wastes resources and annoys customers.

### 2.2 Decision problem (precise)
- **Decision:** For the next campaign, which customers should we call (and in what priority order) given a maximum number of calls `K`?
- **Decision output:** a ranked list + a recommended cut‑off rule.

### 2.3 Objectives, levers, constraints
- **Objective (primary):** maximise **expected net profit** from the campaign (or maximise subscriptions if profit inputs are unavailable).
- **Levers (controllable):** call capacity `K`, decision threshold `t`, prioritisation/ranking rule, agent allocation.
- **Constraints:** limited agents/time, compliance (do‑not‑call), acceptable customer‑experience risk (false positives), budget.

### 2.4 Assumptions (explicit + later used in analysis)
State these on a slide and keep them consistent in the profit calculations:
- `P`: average net profit from one successful subscription (range, not a single number).
- `C`: average cost per outbound call (range).
- **Decision rule:** call if expected value is positive: `P * p̂ − C > 0` ⇒ `p̂ ≥ C/P`.
- Historical patterns generalise sufficiently; acknowledge drift and propose monitoring.

### 2.5 Deliverables (what the stakeholder “gets”)
- **Targeting policy:** “Call top‑K customers ranked by propensity” (for multiple K values).
- **Threshold policy:** “Call if p̂ ≥ t” where `t` is derived from `C/P` and checked with calibration.
- **Business impact summary:** expected conversions/profit vs random targeting.
- **Implementation outline:** scoring workflow + monitoring + retraining cadence.

## 3) Data examination & provenance (targets /30)

### 3.1 Provenance (must cite in slides)
- UCI Machine Learning Repository — **Bank Marketing** (id 222)
- Repository URL: `https://archive.ics.uci.edu/dataset/222/bank+marketing`
- Data URL: `https://archive.ics.uci.edu/static/public/222/data.csv`
- DOI: `10.24432/C5K306`
- Licence: CC BY 4.0
- Access date: include the date you pulled it (in notebook output or slide footnote).

### 3.2 Data snapshot (use in “Data” slide)
- Rows: 45,211
- Features: 16
- Target: `y` (yes/no), positive rate ≈ 11.7% (class imbalance)
- Key missingness patterns:
  - `poutcome` missing for most rows (consistent with `pdays = -1` meaning no prior contact)
  - `contact` missing for many rows (but excluded in Option A)
  - some missing in `education` and `job`

### 3.3 Option A feature availability (“decision moment” slide)
For pre‑call targeting, only include information plausibly known **before** placing the call.

**Exclude (not available pre‑call / depends on campaign execution):**
- `duration` (post‑call; strong leakage)
- `campaign` (contacts made during the current campaign)
- `contact`, `month`, `day_of_week` (describe the last contact scheduling/execution; treat as operational planning, not customer propensity)

**Include (known from CRM prior to calling):**
- Customer attributes: `age`, `job`, `marital`, `education`, `default`, `balance`, `housing`, `loan`
- Prior campaign history: `pdays`, `previous`, `poutcome`

**Why this matters (say explicitly):**
The model must match the real decision point; otherwise performance is inflated and recommendations won’t work operationally.

## 4) Analytics technique & modeling plan (targets /30)

### 4.1 Why classification is fit‑for‑purpose
- Binary outcome (`y`).
- The business needs **ranking + selection** under a capacity constraint.
- Probabilities can be converted into an economically grounded decision rule.

### 4.2 Baseline → improved model ladder (clear and defendable)
1. **Dummy baseline**: always predict “no” (sets a minimum bar).
2. **Logistic regression**: interpretable, stable, good with large tabular data.
3. **Tree‑based model** (one): Random Forest or Gradient Boosting for nonlinearity.

### 4.3 Class imbalance strategy
Because positives are ~11.7%:
- Do **not** lead with accuracy.
- Use PR‑AUC + precision/recall at realistic call capacities.
- Consider `class_weight='balanced'` (logistic) and/or threshold tuning.

### 4.4 Preprocessing pipeline (reproducible scikit‑learn)
Use a single pipeline so results are reproducible and leakage‑resistant:
- **Categorical**: impute missing as `"Missing"` → `OneHotEncoder(handle_unknown='ignore')`
- **Numeric**: median imputation → optional scaling (needed for logistic regression)
- `ColumnTransformer` + `Pipeline` wrapping model

### 4.5 Feature engineering (minimal but high value)
- `prev_contacted = 1(pdays != -1)`
- Optional: `pdays_clean` where `-1 → NaN` so the numeric “days since contact” only applies when meaningful.

### 4.6 Train/test split & tuning (reproducibility requirement)
- Stratified train/test split (e.g., 80/20) with a fixed random seed.
- Cross‑validation on training set for model selection / small hyperparameter search.
- Record: split method, random seed, key hyperparameters.

### 4.7 Calibration (turning scores into business decisions)
Because you will use thresholds and profit calculations:
- Check calibration (reliability curve; Brier score).
- If needed, calibrate probabilities (Platt / isotonic) using validation data and report it.

## 5) Evaluation plan & visuals (targets /30)

### 5.1 Core ML metrics (show in 1 slide)
- PR curve + PR‑AUC (primary)
- ROC‑AUC (secondary)
- Confusion matrix only at the final chosen operating point (after threshold selection rationale)

### 5.2 Decision metrics (what examiners will see as “business translation”)
- **Lift/Gains**: conversions captured in top‑K vs random.
- **Precision@K / Recall@K** at realistic capacities: `K ∈ {1000, 2000, 5000, 10000}` (adapt to your story).
- **Profit curves**:
  - expected profit vs `K` (top‑K selection)
  - expected profit vs threshold `t`

### 5.3 Profit‑based threshold recommendation (clear, professional)
- Assume `P` and `C` (with ranges).
- Use `t = C/P` as the economically justified starting point.
- Validate that threshold choice performs well in terms of profit and serviceable call volume.
- Sensitivity analysis: vary `P` and `C` and show how the best `t`/K changes.

### 5.4 Interpretation (explain drivers without overclaiming)
- Logistic regression: top coefficients (business-readable, with caveats due to one‑hot encoding).
- Tree model: permutation importance (and SHAP only if you can do it cleanly and fast).
- Translate into operational insights (e.g., prior campaign success signals, credit/housing indicators, etc.).

## 6) Recommendations, operationalisation, and reflection (high-score “professional reality”)

### 6.1 Recommendations (must be specific and measurable)
- Deploy propensity scoring; call **top‑K** customers each campaign.
- Use a calibrated threshold linked to economics (`C/P`) when capacity is flexible; otherwise use top‑K.
- Provide expected campaign lift and expected profit under your assumptions.

### 6.2 Operational plan (what you would do at work)
- Weekly/monthly scoring job; export ranked list to CRM; agents call from the top down.
- Monitoring dashboard: conversion rate in called group, score distribution drift, calibration drift.
- Retraining cadence: quarterly or triggered by drift.
- Governance: document data provenance, model versioning, approval process, responsible-use checks.

### 6.3 Limitations (reflective, career-oriented)
- Historic dataset from a specific time/place; risk of drift.
- Option A excludes leakage variables (e.g., `duration`), which lowers performance but preserves decision validity.
- Missing prior-history data for many customers; propose collecting richer CRM features.

## 7) Notebook deliverables checklist (what you must produce)

Your notebook should run end-to-end and output:
- Data summary: rows/features, missingness table, class balance.
- Explicit “feature availability” table: included vs excluded (and why).
- Pipeline + models: dummy, logistic regression, one tree-based model.
- Plots/tables: PR curve, lift/gains, precision@K table, profit curve + sensitivity analysis.
- Interpretation: top drivers (one slide worth).
- Reproducibility block: random seed, split, versions, hyperparameters.

## 8) 10-minute slide plan (mapped to rubric)

Aim for ~9 slides + references.
1. Title + one-sentence pitch + **AI disclosure line**
2. Business challenge (objective, levers, constraints, assumptions)
3. Data provenance + target imbalance + key variables (include licence/DOI)
4. Decision moment & leakage control (Option A; excluded features)
5. Method (pipeline diagram; why classification; model choices)
6. Performance (PR curve + PR‑AUC; calibration check)
7. Business impact (lift/gains + precision@K for realistic capacities)
8. Profit decision rule (threshold `C/P`, profit curve + sensitivity)
9. Recommendations + implementation + risks/limitations + next steps
10. References (or references on each slide + final backup list)

## 9) Executive summary (500 words) outline (so it matches the video)

- Problem + decision + constraints
- Data provenance + target definition + feature availability (Option A)
- Method (pipeline + models + evaluation approach)
- Results (PR‑AUC, lift@K, expected profit under assumptions)
- Recommendations + operationalisation + limitations
- AI disclosure line

## 10) Reproducibility checklist (explicitly report somewhere)

- Dataset link + DOI + licence + access date
- Python + library versions
- Random seed(s)
- Train/test split method
- Included/excluded features list
- Hyperparameters + calibration method (if used)

