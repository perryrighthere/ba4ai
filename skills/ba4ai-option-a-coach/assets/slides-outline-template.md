# BA x AI — Option A (Pre‑Call Targeting) Slide Outline Template (10 minutes)

Keep to ~8–10 slides. Each slide below is a “what you show” + “what you say” prompt.

## Slide 1 — Title / One-sentence pitch / GenAI disclosure

- Show: project title + one-sentence pitch.
- Say: “We build a pre-call propensity model to prioritise who to call under limited capacity.”
- Include: 1-line GenAI disclosure.

## Slide 2 — Business challenge (decision framing)

- Show: decision, objective, levers, constraints, assumptions (`P`, `C`, `K`).
- Say: why wrong targeting is costly and why a ranked call list matters.

## Slide 3 — Data provenance + snapshot

- Show: dataset name/source/DOI/licence/access date; rows/features; base rate.
- Say: what target means (`y` = subscribed) and why imbalance matters.

## Slide 4 — Decision moment & leakage control (Option A)

- Show: included vs excluded features table (and 1-line rationale per exclusion).
- Say: “pre-call only” to keep recommendations implementable.

## Slide 5 — Method (how classification is applied)

- Show: simple pipeline diagram + model ladder (dummy → logistic → tree).
- Say: split strategy, seed, and why PR-AUC / lift@K are the right evaluation lens.

## Slide 6 — Performance (ML metrics)

- Show: PR curve (+ PR-AUC) with base rate; (optional) ROC-AUC.
- Say: interpret PR-AUC in plain language (better-than-random ranking of rare positives).

## Slide 7 — Business impact (capacity targeting)

- Show: precision@K/recall@K/lift@K table for multiple K; gains/lift chart.
- Say: “At K calls, we capture X more subscriptions than random.”

## Slide 8 — Profit decision rule + sensitivity

- Show: profit uplift vs K and/or threshold; small table for 2–3 `(P,C)` scenarios.
- Say: justify `t = C/P`, then show how recommendation changes with assumptions.

## Slide 9 — Recommendations + operational plan + limitations

- Show: final policy (top‑K or threshold), expected uplift, implementation steps, monitoring, risks.
- Say: practical next steps and what you’d do differently with richer CRM data.

## Slide 10 — References

- Show: full reference list (or keep references on each slide and use this as backup).

