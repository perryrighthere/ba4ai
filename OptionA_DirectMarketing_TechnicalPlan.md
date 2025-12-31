# Option A — Detailed Technical Plan (Pre‑Call Targeting)

This technical plan operationalises `OptionA_DirectMarketing_Classification_ProjectPlan.md` into concrete notebook steps, outputs, and checks, while staying aligned with `BA x AI Presentation Brief 2025-26.md` (provenance, assumptions, reproducibility, and business translation).

## 1) Technical outputs you must produce (minimum set)

From a single, reproducible `project.ipynb`, generate:
- Data provenance block (URL/DOI/licence/date accessed) + dataset snapshot (rows/features/class balance).
- “Decision moment” table: included vs excluded features with leakage rationale (Option A).
- A trained pipeline for:
  - Dummy baseline
  - Logistic regression (interpretable)
  - One tree-based model (nonlinear)
- Evaluation artefacts on a held-out test set:
  - PR curve (primary) + PR‑AUC
  - ROC curve + ROC‑AUC (secondary)
  - Calibration curve + Brier score
  - Lift/gains chart
  - Precision@K / Recall@K table for multiple capacities
  - Profit curves vs K and vs threshold, with sensitivity analysis over `(P, C)`
- Model interpretation artefact:
  - Logistic: top coefficients (mapped to business concepts)
  - Tree: permutation importance (top ~10 drivers)
- Reproducibility block: seeds, splits, hyperparameters, library versions.

## 2) Environment & reproducibility setup (do this first)

### 2.1 Notebook settings
- Fix seeds at the top of the notebook:
  - `PYTHONHASHSEED`, `numpy.random.seed`, and model `random_state`.
- Print versions:
  - Python version
  - `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `ucimlrepo`
- Record dataset access timestamp:
  - `datetime.utcnow().isoformat()` and store it in a variable used in your provenance cell.

### 2.2 Dependencies (keep minimal)
- Required: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `ucimlrepo`
- Optional (only if already available / easy to add): `scipy` for minor utilities.
- Avoid adding heavy dependencies unless necessary (time + reproducibility + network constraints).

## 3) Data ingest + provenance cell (assignment alignment)

### 3.1 Fetch data (already started in `project.ipynb`)
- Use `ucimlrepo.fetch_ucirepo(id=222)` and assign:
  - `X_raw = bank_marketing.data.features`
  - `y_raw = bank_marketing.data.targets.iloc[:,0]`

### 3.2 Provenance report (print a compact block)
Include in the notebook output (and reuse in slides):
- Name: “UCI Bank Marketing (id 222)”
- Repository URL, data URL, DOI, licence, access date/time
- Sample size and number of features
- Target definition: `y` indicates subscription to term deposit

## 4) Data examination (EDA) focused on what matters for decisions

### 4.1 Basic quality checks
- `X_raw.shape`, `y_raw.value_counts()`, positive rate.
- Missingness table (count + %) per column (treat `NaN` explicitly).
- Unique value counts for categorical columns.
- Sanity checks:
  - `pdays` contains `-1` (interpreted as “not previously contacted”).
  - Duplicates in rows (expected 0).

### 4.2 Leakage/availability analysis (Option A)
Create an explicit table in the notebook and export it to the slides:
- **Excluded**: `duration`, `campaign`, `contact`, `month`, `day_of_week`
- **Included**: `age`, `job`, `marital`, `education`, `default`, `balance`, `housing`, `loan`, `pdays`, `previous`, `poutcome`
For each excluded feature, include one sentence: “not available pre-call” / “depends on call execution”.

Deliverable: a markdown table rendered in the notebook that you can screenshot into slides.

## 5) Feature engineering & preprocessing (leakage-safe)

### 5.1 Build the Option A feature frame
- `X = X_raw[INCLUDED_COLS].copy()`
- `y = (y_raw == 'yes').astype(int)` (explicit positive class)

### 5.2 Engineer prior-contact features
- `prev_contacted = (X['pdays'] != -1).astype(int)`
- `pdays_clean = X['pdays'].replace(-1, np.nan)` (optional but recommended)
- Keep `previous` and `poutcome` as-is (with missing handled downstream).

### 5.3 Missingness handling strategy
- Categorical (`job`, `education`, `poutcome`, etc.):
  - impute missing with constant `"Missing"` (preferred for transparency).
- Numeric:
  - median impute.

### 5.4 Preprocessing pipeline (scikit-learn)
Use `ColumnTransformer` + `Pipeline` for each model:
- `categorical_cols = [...]` and `numeric_cols = [...]`
- `cat_pipe = SimpleImputer(strategy='constant', fill_value='Missing') -> OneHotEncoder(handle_unknown='ignore')`
- `num_pipe = SimpleImputer(strategy='median') -> (StandardScaler() only for logistic)`

Deliverable: print the final list of feature columns used and the number of one-hot encoded features.

## 6) Data splitting strategy (test set is sacred)

### 6.1 Split design
Use three-way split for clean calibration and tuning:
- Train (60%), validation (20%), test (20%) using stratification.
  - Or: train/test split then cross-validation within train; but a separate validation set helps with calibration and threshold decisions.

### 6.2 What you are allowed to “touch”
- Hyperparameter tuning uses **train** (and CV inside it) and/or **validation**.
- Calibration fitting uses **validation** (or CV-based calibrator).
- Final reported performance and profit/lift use **test only**.

Deliverable: print the split sizes and class balance per split.

## 7) Modeling (baseline → interpretable → strong)

### 7.1 Model 0: Dummy baseline
- `DummyClassifier(strategy='most_frequent')` or `'prior'`.
- Purpose: show why modeling adds value beyond “always no”.

### 7.2 Model 1: Logistic regression (primary interpretable model)
- `LogisticRegression(max_iter=..., class_weight='balanced', solver='liblinear' or 'saga')`
- Tune `C` on train/CV (small grid).
- Output: coefficients + odds-ratio style interpretation (in slides, keep it qualitative).

### 7.3 Model 2: Tree-based model (secondary performance model)
Choose one:
- `HistGradientBoostingClassifier` (fast, strong) OR
- `RandomForestClassifier` (simple, robust).
Tune a small set of parameters (depth/trees/learning rate).

### 7.4 Selection rule
Select “best” model primarily on:
- PR‑AUC on validation
- plus business metrics like precision@K at plausible K (e.g., 5,000)

Deliverable: a model comparison table (PR‑AUC, ROC‑AUC, precision@K).

## 8) Probability calibration (so profit/threshold logic is defensible)

Your business decision rule uses **probabilities** (e.g., call if `P * p̂ − C > 0` ⇔ `p̂ ≥ C/P`). That only makes sense if `p̂` is reasonably **calibrated** (a score of 0.20 should mean “~20% of similar customers convert”).

### 8.1 Diagnose calibration
- Do this **before choosing** a profit threshold, and do it on **validation** (not the test set).
- Produce a reliability diagram:
  - `sklearn.calibration.CalibrationDisplay.from_estimator(model, X_val, y_val, n_bins=10, strategy="quantile")`
  - Use `"quantile"` bins so each bin has similar sample size (more stable with imbalance).
- Report a proper scoring rule:
  - **Brier score** (`sklearn.metrics.brier_score_loss(y_val, p̂_val)`) — lower is better.
- Optional (nice-to-have, not required): calibration-in-the-large (mean `p̂` vs base rate) and a short note if probabilities are systematically too high/low.

Deliverable (slide-ready): one reliability curve + a small table with `Brier` and base rate on validation.

### 8.2 Calibrate if needed
- Default recommendation for this project: **Platt scaling** (`method="sigmoid"`) because it is robust and less prone to overfitting than isotonic.
- Consider **isotonic** (`method="isotonic"`) only if you have a large calibration set and the reliability curve shows clear non-linearity (and you can show it improves Brier without hurting lift@K materially).

Two defensible fitting patterns (pick one and be explicit in the notebook for reproducibility):

**Pattern A — CV calibration on training (cleanest separation):**
- Use only `train` for fitting + calibration via CV:
  - `CalibratedClassifierCV(estimator=base_pipeline, method="sigmoid", cv=5)` then `.fit(X_train, y_train)`
- Use `validation` only for model selection/threshold selection and reporting calibration diagnostics (and `test` only for the final report).

**Pattern B — Prefit + calibrate on validation (simple and common):**
- Fit the chosen model on `train`, then calibrate using `validation`:
  - `base_model.fit(X_train, y_train)`
  - `cal = CalibratedClassifierCV(estimator=base_model, method="sigmoid", cv="prefit")`
  - `cal.fit(X_val, y_val)`
- After calibration, use `cal.predict_proba(...)` everywhere you use `p̂`.
- Note: this couples calibration and validation; mitigate by keeping **test** completely untouched for final metrics.

After calibration:
- Re-plot the reliability curve on validation.
- Recompute Brier score on validation.
- Sanity-check that ranking metrics did not collapse (PR‑AUC and lift@K should be similar; calibration may slightly change them).

Deliverable: show “before vs after” calibration curves for the chosen model (one slide worth).

## 9) Evaluation on test set (metrics + business translation)

This section produces the **final, reportable** results. Keep the logic strict:
- Do **not** tune hyperparameters, calibration, thresholds, or choose K using the test set.
- Freeze these using training/validation (Steps 7–8), then evaluate **once** on test.

Assumption for Step 9: you have `MODEL_CALIBRATED` from Step 8. If you skip calibration, avoid recommending a probability threshold policy and focus on top‑K ranking only.

### 9.0 Freeze the decision policy (before looking at test)
Pick one (both are acceptable; state which you use):
- **Capacity fixed (top‑K):** choose `K*` based on operational capacity (e.g., number of calls per campaign). If you don’t have a real K, pick a plausible range and justify it (e.g., 1k/2k/5k/10k).
- **Capacity flexible (threshold):** choose scenarios for `(P, C)` and set `t = C/P`. Optionally check a small neighbourhood around `t` on **validation** to ensure it is not clearly dominated in expected profit.

Record in the notebook:
- chosen `K*` (or list of K values), chosen `(P, C)` grid, chosen `t` (or list of `t = C/P`).

### 9.1 Standard ML evaluation (test set)
On the **test set**, compute predicted probabilities and headline ML metrics:
- `p̂_test = MODEL_CALIBRATED.predict_proba(X_test)[:,1]`
- PR curve + PR‑AUC (primary): `precision_recall_curve`, `average_precision_score`
- ROC curve + ROC‑AUC (secondary): `roc_curve`, `roc_auc_score`

Deliverables:
- PR curve with PR‑AUC and base rate annotated.
- A small table: PR‑AUC, ROC‑AUC, test base rate.

### 9.2 Capacity-based targeting (top‑K)
Compute for multiple capacities `K`:
- Sort customers by `p̂_test` descending.
- For each `K`:
  - `TP_K = sum(y_true in top-K)`
  - `precision@K = TP_K / K`
  - `recall@K = TP_K / total_positives`
  - **lift@K = precision@K / base_rate**

Also report an intuitive “business delta” vs random targeting:
- `expected_positives_random = K * base_rate`
- `incremental_positives = TP_K − expected_positives_random`

Deliverables:
- Table for `K ∈ {1000, 2000, 5000, 10000}` (adjust to your narrative).
- Gains curve / lift chart figure.

### 9.3 Profit analysis (threshold and top‑K)
Define scenario parameters (explicit assumptions; justify with one sentence in slides):
- Profit per success `P` (e.g., £200, £500, £1000)
- Cost per call `C` (e.g., £2, £5, £10)

Compute both versions for transparency (use the same policy frozen in 9.0):
- **Realised profit (uses actual `y_test`):** `profit_realised = TP*P − N_calls*C`
- **Expected profit (uses `p̂_test`):** `profit_expected = Σ(p̂_called)*P − N_calls*C`

Compute a baseline so uplift is meaningful:
- **Random targeting baseline:** expected conversions `K*base_rate` and expected profit `K*(base_rate*P − C)`
- Optional: “call nobody” baseline profit = 0.

Profit for top‑K (capacity fixed):
- For each `K` and each `(P, C)`: call top‑K by `p̂_test`, compute `TP_K`, realised/expected profit, and profit uplift vs random.

Profit for threshold policy (capacity flexible):
- For each `(P, C)` compute `t = C/P` and call if `p̂_test ≥ t`.
- Report resulting call volume, conversions, realised/expected profit, and uplift.

Important: if you sweep thresholds to draw a “profit vs threshold” curve, use it as a **descriptive out-of-sample check**; do not choose the final `t` by maximising test profit.

Deliverables:
- Profit vs K plot (for a few `(P,C)` scenarios).
- Profit vs threshold plot (sweep thresholds).
- A sensitivity “heatmap” or small table summarising the recommended `t=C/P` impact.

Deliverable (one-slide version that scores well):
- A compact table for 3 scenarios (e.g., `(P,C) = (200,5), (500,5), (1000,10)`) showing: `K or t`, calls made, conversions, lift, and realised profit uplift vs random.

## 10) Model interpretation (turn into business recommendations)

### 10.1 Logistic regression interpretation
- Extract feature names from the one‑hot encoder.
- List top positive and top negative coefficients (top 8–12).
- Translate into business language (e.g., “prior campaign success” signal, “credit/default indicators”, “loan status”).

### 10.2 Tree model interpretation (if chosen)
- Use permutation importance on test or validation set.
- Plot top ~10 features.

Deliverable: one clean chart + 3–5 bullet insights that support recommendations.

## 11) Final recommendation logic (what you will say in the video)

Your final answer must include a decision policy:
- **If capacity is fixed:** “Call top‑K ranked customers (K = operational capacity).”
- **If capacity is flexible:** “Call if `p̂ ≥ t`, with `t` justified by `t = C/P` and validated by profit curves.”

Include:
- Expected incremental conversions vs random targeting for the chosen K.
- Expected profit uplift under the chosen `(P,C)` range.
- A short implementation plan (how to run scoring + monitoring).

## 12) Slide-ready artefacts checklist (keep it within 10 minutes)

Prepare these figures/tables as notebook outputs you can paste into slides:
- Problem framing (1 slide)
- Data provenance + class balance + missingness highlights (1 slide)
- Feature availability (included/excluded) (1 slide)
- Method pipeline diagram (1 slide; can be a simple box diagram)
- PR curve + key metrics (1 slide)
- Lift/gains + precision@K table (1 slide)
- Profit curve + sensitivity analysis (1 slide)
- Recommendations + ops plan + limitations (1 slide)
- References + AI disclosure (on slide or final slide)

## 13) Guardrails (common mistakes to avoid)

- Do not use `duration` (or other post-call fields) in the main Option A model.
- Do not report results only on training data; final metrics must be on a held-out test set.
- Do not use accuracy as the headline metric; use PR‑AUC and capacity/profit metrics.
- Do not omit provenance/licence/date accessed; include them in notebook + slides.
- Do not omit the 1‑line GenAI disclosure in the video/slide deck.

## 14) “Definition of done” (technical)

You are finished when:
- `project.ipynb` runs end-to-end without manual intervention and reproduces the same results (given fixed seeds).
- You can answer, with numbers and plots, “How many more subscriptions and how much more expected profit do we get if we call top‑K vs random?”
- You have 8–10 slides that match the required 3 sections: business challenge → technique application → interpretation/recommendations, within 10 minutes.
