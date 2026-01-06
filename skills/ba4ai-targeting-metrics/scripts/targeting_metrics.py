from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


def _as_numpy_1d(a) -> np.ndarray:
    arr = np.asarray(a)
    if arr.ndim != 1:
        raise ValueError(f"Expected 1D array, got shape={arr.shape}")
    return arr


def base_rate(y_true) -> float:
    y = _as_numpy_1d(y_true).astype(float)
    if len(y) == 0:
        raise ValueError("y_true is empty")
    if not np.isin(y, [0.0, 1.0]).all():
        raise ValueError("y_true must be binary 0/1")
    return float(y.mean())


@dataclass(frozen=True)
class KMetricsRow:
    k: int
    tp_at_k: int
    precision_at_k: float
    recall_at_k: float
    lift_at_k: float
    expected_positives_random: float
    incremental_positives_vs_random: float


def k_metrics_table(y_true, p_hat, k_list: Sequence[int]) -> list[KMetricsRow]:
    y = _as_numpy_1d(y_true).astype(int)
    p = _as_numpy_1d(p_hat).astype(float)
    if len(y) != len(p):
        raise ValueError("y_true and p_hat must have the same length")
    if len(y) == 0:
        raise ValueError("Inputs are empty")

    br = base_rate(y)
    order = np.argsort(-p, kind="mergesort")
    y_sorted = y[order]
    total_pos = int(y.sum())

    rows: list[KMetricsRow] = []
    for k in k_list:
        if k <= 0:
            raise ValueError("All K must be positive")
        k_eff = min(int(k), len(y_sorted))
        tp = int(y_sorted[:k_eff].sum())
        precision = tp / k_eff if k_eff else 0.0
        recall = tp / total_pos if total_pos else 0.0
        lift = (precision / br) if br > 0 else float("nan")
        expected_random = k_eff * br
        inc = tp - expected_random
        rows.append(
            KMetricsRow(
                k=k_eff,
                tp_at_k=tp,
                precision_at_k=float(precision),
                recall_at_k=float(recall),
                lift_at_k=float(lift),
                expected_positives_random=float(expected_random),
                incremental_positives_vs_random=float(inc),
            )
        )
    return rows


@dataclass(frozen=True)
class ProfitRow:
    policy: str  # "topk" or "threshold"
    k: int | None
    threshold: float | None
    p_success: float
    c_call: float
    calls_made: int
    tp: int
    profit_realised: float
    profit_expected: float
    profit_expected_random_baseline: float
    profit_expected_uplift_vs_random: float


def _profit_random_baseline_expected(br: float, calls: int, p_success: float, c_call: float) -> float:
    return calls * (br * p_success - c_call)


def profit_topk_table(
    y_true,
    p_hat,
    k_list: Sequence[int],
    p_success_list: Sequence[float],
    c_call_list: Sequence[float],
) -> list[ProfitRow]:
    y = _as_numpy_1d(y_true).astype(int)
    p = _as_numpy_1d(p_hat).astype(float)
    if len(y) != len(p):
        raise ValueError("y_true and p_hat must have the same length")
    br = base_rate(y)

    order = np.argsort(-p, kind="mergesort")
    y_sorted = y[order]
    p_sorted = p[order]

    rows: list[ProfitRow] = []
    for k in k_list:
        if k <= 0:
            raise ValueError("All K must be positive")
        calls = min(int(k), len(y_sorted))
        tp = int(y_sorted[:calls].sum())
        expected_conversions = float(p_sorted[:calls].sum())
        for p_success in p_success_list:
            for c_call in c_call_list:
                realised = tp * p_success - calls * c_call
                expected = expected_conversions * p_success - calls * c_call
                random_expected = _profit_random_baseline_expected(br, calls, p_success, c_call)
                rows.append(
                    ProfitRow(
                        policy="topk",
                        k=calls,
                        threshold=None,
                        p_success=float(p_success),
                        c_call=float(c_call),
                        calls_made=calls,
                        tp=tp,
                        profit_realised=float(realised),
                        profit_expected=float(expected),
                        profit_expected_random_baseline=float(random_expected),
                        profit_expected_uplift_vs_random=float(expected - random_expected),
                    )
                )
    return rows


def profit_threshold_table(
    y_true,
    p_hat,
    p_success_list: Sequence[float],
    c_call_list: Sequence[float],
) -> list[ProfitRow]:
    y = _as_numpy_1d(y_true).astype(int)
    p = _as_numpy_1d(p_hat).astype(float)
    if len(y) != len(p):
        raise ValueError("y_true and p_hat must have the same length")
    br = base_rate(y)

    rows: list[ProfitRow] = []
    for p_success in p_success_list:
        for c_call in c_call_list:
            if p_success <= 0:
                raise ValueError("p_success must be > 0")
            threshold = c_call / p_success
            called = p >= threshold
            calls = int(called.sum())
            tp = int(y[called].sum())
            expected_conversions = float(p[called].sum())
            realised = tp * p_success - calls * c_call
            expected = expected_conversions * p_success - calls * c_call
            random_expected = _profit_random_baseline_expected(br, calls, p_success, c_call)
            rows.append(
                ProfitRow(
                    policy="threshold",
                    k=None,
                    threshold=float(threshold),
                    p_success=float(p_success),
                    c_call=float(c_call),
                    calls_made=calls,
                    tp=tp,
                    profit_realised=float(realised),
                    profit_expected=float(expected),
                    profit_expected_random_baseline=float(random_expected),
                    profit_expected_uplift_vs_random=float(expected - random_expected),
                )
            )
    return rows


def to_dicts(rows: Iterable[object]) -> list[dict]:
    out: list[dict] = []
    for r in rows:
        if hasattr(r, "__dict__"):
            out.append(dict(r.__dict__))
        else:
            raise TypeError(f"Row is not a dataclass-like object: {type(r)}")
    return out

