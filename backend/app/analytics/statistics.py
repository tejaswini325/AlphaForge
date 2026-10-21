import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

def statistics_report(prices: pd.DataFrame) -> dict:
    returns = prices.pct_change(fill_method=None).dropna(how="all")
    out = {
        "annualized_volatility": (returns.std() * np.sqrt(252)).replace([np.inf, -np.inf], np.nan).fillna(0).to_dict(),
        "mean_daily_return": returns.mean().fillna(0).to_dict(),
        "correlation": returns.corr().fillna(0).round(4).to_dict(),
        "adf_returns": {}
    }
    for col in returns:
        s = returns[col].dropna()
        if len(s) < 25 or s.nunique() < 2:
            out["adf_returns"][col] = {"status": "insufficient_or_constant_series"}
            continue
        try:
            stat, p, lag, nobs, *_ = adfuller(s, autolag="AIC")
            out["adf_returns"][col] = {"statistic": float(stat), "p_value": float(p), "used_lag": int(lag), "nobs": int(nobs), "null": "series has a unit root"}
        except Exception as exc:
            out["adf_returns"][col] = {"status": f"test_failed: {type(exc).__name__}"}
    return out

def performance_metrics(returns: pd.Series, benchmark: pd.Series | None = None, risk_free_annual: float = 0.02) -> dict:
    r = pd.Series(returns).dropna().astype(float)
    if r.empty:
        raise ValueError("At least one valid return is required.")
    rf_daily = (1 + risk_free_annual) ** (1 / 252) - 1
    excess = r - rf_daily
    wealth = (1 + r).cumprod()
    peak = wealth.cummax()
    dd = wealth / peak - 1
    vol = float(r.std(ddof=1) * np.sqrt(252)) if len(r) > 1 else 0.0
    sharpe = float(excess.mean() / r.std(ddof=1) * np.sqrt(252)) if len(r) > 1 and r.std(ddof=1) > 0 else 0.0
    downside = np.minimum(excess.to_numpy(), 0)
    downside_dev = float(np.sqrt(np.mean(downside ** 2)) * np.sqrt(252))
    cagr = float(wealth.iloc[-1] ** (252 / len(r)) - 1) if wealth.iloc[-1] > 0 else -1.0
    result = {"observations": len(r), "cumulative_return": float(wealth.iloc[-1] - 1), "annualized_return": cagr, "annualized_volatility": vol, "sharpe_ratio": sharpe, "sortino_ratio": float(excess.mean() * 252 / downside_dev) if downside_dev > 0 else 0.0, "max_drawdown": float(dd.min()), "calmar_ratio": float(cagr / abs(dd.min())) if dd.min() < 0 else 0.0}
    if benchmark is not None:
        aligned = pd.concat([r.rename("portfolio"), benchmark.rename("benchmark")], axis=1).dropna()
        active = aligned.portfolio - aligned.benchmark
        tracking = active.std(ddof=1) * np.sqrt(252) if len(active) > 1 else 0
        result["benchmark_cumulative_return"] = float((1 + aligned.benchmark).prod() - 1) if len(aligned) else None
        result["information_ratio"] = float(active.mean() * 252 / tracking) if tracking > 0 else 0.0
    return result
