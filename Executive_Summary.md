# Executive Summary — Option A: Pre‑Call Targeting for Bank Telemarketing (≤500 words)

## 1) Problem and decision

Outbound telemarketing for term deposits is costly and capacity‑constrained: agent time is limited and poorly targeted calls waste budget and harm customer experience. The decision is **who to call next** (ranked list + cut‑off) under calling capacity **K**, with the objective of maximising expected campaign value (profit, or conversions when profit inputs are unavailable) under operational and compliance constraints.

## 2) Data and provenance

We use the UCI Machine Learning Repository **Bank Marketing** dataset (id=222; DOI **10.24432/C5K306**; licence **CC BY 4.0**; accessed **2026‑01‑07 UTC**). It contains **45,211** records, **16** features, and a binary target **y** (subscribed: yes/no) with base rate ≈ **11.7%**. To keep recommendations implementable at the **pre‑call** decision moment, we exclude post‑call/execution variables (especially `duration`) and use only pre‑call CRM/prior‑history signals.

## 3) Method (analytics technique)

Classification is fit‑for‑purpose because the outcome is binary and the business action is “rank and select under capacity.” We trained a defensible ladder (dummy baseline, logistic regression, random forest) using a single scikit‑learn pipeline (imputation + one‑hot encoding + model). We used a stratified **60/20/20** train/validation/test split with seed **42**, selected the final model by validation PR‑AUC, and calibrated probabilities for decision‑making using **isotonic calibration** (5‑fold CV on training only).

## 4) Results (business translation)

On the held‑out test set, the selected **random forest + isotonic calibration** achieved **PR‑AUC = 0.379** versus base rate **0.117**, supporting strong ranking for rare positives. Capacity targeting delivers meaningful lift: calling the top **1,000** customers yields **precision@1,000 = 0.417** (lift **3.56×**), capturing ~**300** more subscriptions than random calling; at **K=5,000**, precision is **0.167** (lift **1.43×**) with ~**251** incremental subscriptions vs random. Translating this into economics (explicit assumptions), calling the top **5,000** customers produces large expected profit uplift vs random targeting, e.g. **~£51.6k** (P=£200 per success, C=£5 per call) and **~£128.9k** (P=£500, C=£5); results scale with (P, C) and should be reported as sensitivity scenarios, not single “true” values.

## 5) Recommendation and implementation

Recommendation: deploy propensity scoring and **call the top‑K customers** each campaign (K set by operational capacity), using calibrated probabilities for threshold **t=C/P** and profit scenarios. Operationally, run a scoring job, export a ranked call list to the CRM, and have agents call from the top down; monitor conversion rate, score drift, and calibration drift, and retrain on a cadence (e.g., quarterly) or when drift is detected. Key limitations are dataset/time‑period drift risk, incomplete CRM signals (limited prior history for many customers), and reliance on profit/cost assumptions—so governance and monitoring are required for a production rollout.

## 6) GenAI disclosure (one line)

GenAI disclosure: I used AI tools (Codex/ChatGPT) to help structure the analysis workflow and improve code/wording clarity; all modelling, metrics, and references were produced/validated from reproduced runs.
