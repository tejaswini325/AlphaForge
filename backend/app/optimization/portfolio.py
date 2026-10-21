from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.optimize import minimize

def optimize_weights(returns: pd.DataFrame, strategy: str = "inverse_volatility", max_weight: float = 0.25, risk_aversion: float = 5.0, forecasts: dict[str, float] | None = None, long_only: bool = True) -> dict:
    if returns.empty or returns.shape[1] == 0:
        raise ValueError("Returns must contain at least one asset.")
    if not 0 < max_weight <= 1:
        raise ValueError("max_weight must be in (0, 1].")
    clean = returns.replace([np.inf, -np.inf], np.nan).dropna(axis=0, how="any")
    if len(clean) < 20:
        raise ValueError("At least 20 complete return rows are required.")
    assets = list(clean.columns)
    n = len(assets)
    if n * max_weight < 1 - 1e-8:
        raise ValueError("Infeasible constraints: asset count × max_weight must be at least 1.")
    cov = clean.cov().to_numpy() * 252
    cov = cov + np.eye(n) * max(float(np.trace(cov) / max(n,1)) * 1e-6, 1e-10)
    means = clean.mean().to_numpy() * 252
    if strategy == "equal_weight":
        w = np.ones(n) / n
    elif strategy == "inverse_volatility":
        inv = 1 / np.maximum(np.sqrt(np.diag(cov)), 1e-8)
        w = inv / inv.sum()
    elif strategy in {"minimum_variance", "mean_variance", "signal_driven"}:
        mu = means.copy()
        if strategy == "signal_driven" and forecasts:
            mu = np.array([float(forecasts.get(a, 0.0)) * 252 for a in assets])
        def objective(x):
            variance = x @ cov @ x
            return variance if strategy == "minimum_variance" else risk_aversion * variance - mu @ x
        bounds = [(0, max_weight) if long_only else (-max_weight, max_weight)] * n
        result = minimize(objective, np.ones(n)/n, method="SLSQP", bounds=bounds, constraints=[{"type":"eq", "fun":lambda x: np.sum(x)-1}], options={"maxiter":1000, "ftol":1e-12})
        if not result.success:
            raise ValueError(f"Optimization failed or constraints are infeasible: {result.message}")
        w = result.x
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    if long_only:
        w = np.clip(w, 0, None)
    w = w / w.sum()
    if np.max(w) > max_weight + 1e-5:
        # Feasible capped-simplex projection.
        w = np.minimum(w, max_weight)
        for _ in range(100):
            excess = 1 - w.sum()
            free = w < max_weight - 1e-10
            if abs(excess) < 1e-10 or not free.any(): break
            w[free] += excess / free.sum()
            w = np.clip(w, 0, max_weight)
    return {"weights": {a: float(v) for a,v in zip(assets,w)}, "expected_annual_return_estimate": float(w @ means), "annualized_volatility_estimate": float(np.sqrt(max(w @ cov @ w,0))), "constraints": {"sum_weights": float(w.sum()), "long_only": long_only, "max_weight": max_weight, "max_observed_weight": float(w.max())}, "strategy": strategy}
