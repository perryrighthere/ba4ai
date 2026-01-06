---
name: ba4ai-targeting-metrics
description: Compute and present targeting metrics for propensity models in the BA x AI Option A direct-marketing project (UCI Bank Marketing id=222): PR-AUC, precision@K/recall@K/lift@K, gains, calibration diagnostics, and profit analysis for top-K and threshold policies (t=C/P). Use when you need slide-ready tables/plots that translate model scores into business decisions under call-capacity and cost/profit assumptions.
---

# Targeting Metrics (lift@K + profit + calibration)

Use this skill when you already have a trained model that outputs probabilities `p̂` and you need **decision-grade** evaluation and visuals.

## Inputs you must define (explicit assumptions)

- `y_true`: 0/1 outcome (1 = subscribed).
- `p_hat`: predicted probability `P(y=1)`.
- Capacities `K_list` (e.g., `[1000, 2000, 5000, 10000]`).
- Economic assumptions:
  - profit per success `P`
  - cost per call `C`
- Baselines:
  - random targeting (uses base rate)
  - optional “call nobody” baseline profit = 0

## What to compute (slide-ready)

1. **PR curve + PR-AUC** (annotate base rate).
2. **Precision@K / Recall@K / Lift@K** table for your `K_list`.
3. **Incremental positives vs random** at each K.
4. **Profit uplift vs random** for:
   - top‑K policy (capacity fixed)
   - threshold policy (capacity flexible), with `t = C/P`
5. **Calibration check** (reliability curve + Brier score) if you plan to use a threshold rule.

## Use the bundled script (recommended)

Because the skill folder name contains hyphens, import the helper module by file path inside `project.ipynb` (or any Python file):

```python
import importlib.util
import sys
from pathlib import Path

path = Path("skills/ba4ai-targeting-metrics/scripts/targeting_metrics.py")
spec = importlib.util.spec_from_file_location("targeting_metrics", path)
tm = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = tm
assert spec.loader is not None
spec.loader.exec_module(tm)
```

Then use the helpers to avoid re-implementing formulas:

- `scripts/targeting_metrics.py`:
  - `k_metrics_table(...)` → precision@K/recall@K/lift@K + incremental positives
  - `profit_topk_table(...)` → realised/expected profit + uplift vs random for each `(P,C)` and K
  - `profit_threshold_table(...)` → call volume + profit for `t=C/P` per `(P,C)`

If you create plots, keep them simple and readable (one chart per slide).
