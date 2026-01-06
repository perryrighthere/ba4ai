# Option A (Pre‑Call Targeting) — scope and leakage guardrails

Goal: decide **who to call before any call is placed**.

## Decision moment: what features are allowed?

Only use information plausibly available **pre‑call**.

### Exclude (leakage / depends on campaign execution)

- `duration` (post-call outcome proxy; leaks target)
- `campaign` (current campaign contact count; depends on execution)
- `contact`, `month`, `day_of_week` (operational scheduling/execution variables; treat as out of scope for “customer propensity” in Option A)

### Include (CRM / prior history pre-call)

- Customer attributes: `age`, `job`, `marital`, `education`, `default`, `balance`, `housing`, `loan`
- Prior campaign history: `pdays`, `previous`, `poutcome`

## Required storytelling note (why you excluded fields)

Say explicitly:
- “We exclude post-call / execution fields to match the real decision point; otherwise performance is inflated and recommendations won’t work operationally.”

## Metrics that fit the decision (avoid common traps)

- Avoid leading with accuracy (class imbalance).
- Prefer:
  - PR curve + PR-AUC
  - precision@K / recall@K / lift@K for realistic call capacities
  - profit uplift vs random targeting under explicit `(P, C)` assumptions

