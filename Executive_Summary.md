# Executive Summary — Option A: Pre‑Call Targeting for Bank Telemarketing

## 1) Problem and decision

Outbound telemarketing for term deposits is costly and capacity‑constrained: agent time is limited and poorly targeted calls waste budget and harm customer experience. This project frames the challenge as a decision problem: **who to call next (and in what order)** given a calling capacity **K**. The objective is to maximise expected campaign value (profit, or conversions if profit inputs are unavailable) under operational and compliance constraints.

## 2) Data and provenance

We use the UCI Machine Learning Repository **Bank Marketing** dataset (id=222; DOI **10.24432/C5K306**; licence **CC BY 4.0**; accessed **2026‑01‑07 UTC**): **45,211** records and a binary target **y** (subscribed yes/no) with base rate ≈ **11.7%**. To match the **pre‑call** decision moment, we exclude post‑call/execution fields (especially `duration`) and use only pre‑call CRM/prior‑history signals.

## 3) Method (analytics technique)

Classification is fit‑for‑purpose because the outcome is binary and the action is “rank and select under capacity.” We trained a defensible ladder (dummy baseline, logistic regression, random forest) using a single scikit‑learn pipeline (imputation + one‑hot encoding + model) with a stratified **60/20/20** train/validation/test split (seed **42**). We selected the final model by validation PR‑AUC and calibrated probabilities using **isotonic calibration** (5‑fold CV on training only).

## 4) Results (business translation)

On the held‑out test set, the selected **random forest + isotonic calibration** achieved **PR‑AUC = 0.379** versus base rate **0.117**. Capacity targeting delivers material lift: calling the top **1,000** customers yields **precision@1,000 = 0.417** (lift **3.56×**) and ~**300** incremental subscriptions versus random calling; at **K=5,000**, precision is **0.167** (lift **1.43×**) with ~**251** incremental subscriptions. Under explicit economic assumptions, the expected profit uplift at **K=5,000** is **~£51.6k** (P=£200, C=£5) and **~£128.9k** (P=£500, C=£5); results should be reported as sensitivity to (P, C).

## 5) Recommendation and implementation

Recommendation: deploy propensity scoring and **call the top‑K customers** each campaign (K set by operational capacity). Where capacity is flexible, use calibrated probabilities with threshold logic **t=C/P** and validate that resulting call volumes are feasible. Operationally, run a scheduled scoring job, export a ranked call list to the CRM, and have agents call from the top down; monitor conversion rate, score drift, and calibration drift; retrain on a cadence (e.g., quarterly) or when drift triggers occur. Key limitations are concept drift risk, limited prior‑history signals for many customers, and reliance on assumed profit/cost inputs.

## 6) GenAI disclosure (one line)

GenAI disclosure: I used AI tools (Codex/ChatGPT) to help structure the workflow and improve code/writing clarity; all results and references were verified from reproduced runs.
