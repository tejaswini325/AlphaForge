from __future__ import annotations
import pandas as pd
import numpy as np
from app.analytics.statistics import performance_metrics
from app.optimization.portfolio import optimize_weights

def run_backtest(prices: pd.DataFrame, strategy: str = "equal_weight", benchmark: str | None = None, initial_capital: float = 100000, rebalance_every: int = 21, transaction_cost_bps: float = 8, slippage_bps: float = 2, max_weight: float = 0.25, risk_aversion: float = 5.0, lookback: int = 126) -> dict:
    if prices.empty or prices.shape[1] == 0:
        raise ValueError("Price data must not be empty.")
    if initial_capital <= 0 or rebalance_every < 1 or transaction_cost_bps < 0 or slippage_bps < 0:
        raise ValueError("Capital must be positive; rebalance interval must be >=1; costs must be nonnegative.")
    prices = prices.sort_index().replace([np.inf,-np.inf], np.nan).dropna(axis=1, how="all")
    returns = prices.pct_change(fill_method=None)
    assets = [c for c in prices.columns if c != benchmark]
    if not assets:
        raise ValueError("No investable assets remain after excluding benchmark.")
    portfolio_returns, turnovers, costs, weights_log, dates = [], [], [], [], []
    previous = pd.Series(0.0, index=assets)
    current = pd.Series(0.0, index=assets)
    for i in range(1, len(prices)):
        # Decision is made after close i-1 using only returns ending at i-1.
        if (i - 1) % rebalance_every == 0:
            history = returns[assets].iloc[max(1, i-lookback):i].dropna(how="any")
            if len(history) >= 20:
                try:
                    result = optimize_weights(history, strategy=strategy, max_weight=max_weight, risk_aversion=risk_aversion)
                    current = pd.Series(result["weights"]).reindex(assets).fillna(0.0)
                except ValueError:
                    current = pd.Series(1/len(assets), index=assets)
            else:
                current = pd.Series(1/len(assets), index=assets)
            traded = (current - previous).abs().sum()
            turnover = float(traded / 2) # one-way turnover convention
            cost = turnover * (transaction_cost_bps + slippage_bps) / 10000
            previous = current.copy()
        else:
            turnover, cost = 0.0, 0.0
        day = returns[assets].iloc[i].fillna(0.0)
        gross = float((current * day).sum())
        net = (1 + gross) * (1 - cost) - 1
        portfolio_returns.append(net)
        turnovers.append(turnover)
        costs.append(cost)
        weights_log.append(current.to_dict())
        dates.append(prices.index[i])
    r = pd.Series(portfolio_returns, index=pd.DatetimeIndex(dates), name="portfolio")
    b = returns[benchmark].reindex(r.index) if benchmark and benchmark in returns.columns else None
    metrics = performance_metrics(r, b)
    equity = initial_capital * (1+r).cumprod()
    return {"strategy": strategy, "benchmark": benchmark, "initial_capital": initial_capital, "metrics": metrics, "series": [{"date":str(d.date()),"return":float(v),"equity":float(e),"turnover_one_way":float(t),"transaction_cost_fraction":float(c)} for d,v,e,t,c in zip(r.index,r,equity,turnovers,costs)], "rebalancing_weights": [{"date":str(d.date()),"weights":w} for d,w in zip(r.index,weights_log)], "cost_convention": "one-way turnover = sum(abs(target-current))/2; cost fraction = one-way turnover × (transaction_cost_bps + slippage_bps)/10000; charged once on rebalance dates", "gross_net_note": "Returned series are net of estimated transaction costs and slippage."}
