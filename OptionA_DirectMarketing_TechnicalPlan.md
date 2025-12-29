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

### 8.1 Diagnose calibration
- Use `sklearn.calibration.CalibrationDisplay.from_estimator`.
- Compute Brier score on validation and test.

### 8.2 Calibrate if needed
- Use `CalibratedClassifierCV(base_estimator=..., method='sigmoid' or 'isotonic', cv=...)`
- Fit calibrator using train+validation (or CV on train).
- Re-check calibration curve.

Deliverable: show “before vs after” calibration curves for the chosen model (one slide worth).

## 9) Evaluation on test set (metrics + business translation)

### 9.1 Standard ML evaluation
On test set:
- PR curve + PR‑AUC
- ROC curve + ROC‑AUC
- Choose an operating threshold only after the profit/capacity analysis.

### 9.2 Capacity-based targeting (top‑K)
Compute for multiple capacities `K`:
- Sort customers by `p̂` descending.
- For each `K`:
  - `TP_K = sum(y_true in top-K)`
  - `precision@K = TP_K / K`
  - `recall@K = TP_K / total_positives`
  - **lift@K = precision@K / base_rate**

Deliverables:
- Table for `K ∈ {1000, 2000, 5000, 10000}` (adjust to your narrative).
- Gains curve / lift chart figure.

### 9.3 Profit analysis (threshold and top‑K)
Define scenario parameters (explicit assumptions):
- Profit per success `P` (e.g., £200, £500, £1000)
- Cost per call `C` (e.g., £2, £5, £10)

Compute two versions for transparency:
- **Realised profit (uses actual y on test):** `profit = TP*P − N_calls*C`
- **Expected profit (uses probabilities):** `profit = sum(p̂)*P − N_calls*C` (useful for decision-making story)

Deliverables:
- Profit vs K plot (for a few `(P,C)` scenarios).
- Profit vs threshold plot (sweep thresholds).
- A sensitivity “heatmap” or small table summarising the recommended `t=C/P` impact.

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

