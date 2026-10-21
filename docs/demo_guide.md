# AlphaForge demo guide

1. Start the API and frontend using README commands.
2. Confirm `/health` and open `/docs`.
3. Overview: run equal-weight backtest, record cumulative return, Sharpe, max drawdown, and equity curve.
4. Change transaction costs and rerun. Explain one-way turnover and the simplified proportional cost assumption.
5. Alpha Research: train models, compare to zero-return baseline, and point out chronological test dates.
6. Optimization: run inverse-volatility or minimum variance; verify weights sum to one and caps hold.
7. Risk Analytics: inspect correlation and volatility; discuss estimation instability.
8. Experiments: show persisted runs.
9. Be explicit that the default series are synthetic. If using real tickers, disclose data provider and sample period.
10. Explain one limitation and one future improvement, such as point-in-time constituents or walk-forward retraining.
