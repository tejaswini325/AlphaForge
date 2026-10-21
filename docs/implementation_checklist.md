# Implementation checklist

## Completed and verified
- [x] Workspace inspected; no existing project needed preservation.
- [x] Modular FastAPI backend and Pydantic request validation.
- [x] Deterministic synthetic data and optional yfinance adapter.
- [x] Price validation, quality report, return/rolling feature construction.
- [x] Descriptive statistics, correlation and guarded ADF tests.
- [x] Chronological baseline model comparison with a held-out test period.
- [x] Equal-weight, inverse-volatility, minimum-variance and mean-variance strategies.
- [x] Backtest loop with prior-period information, turnover, costs and slippage.
- [x] Risk/performance metrics and optional benchmark comparison.
- [x] SQLAlchemy experiment metadata persistence, SQLite default and PostgreSQL Compose configuration.
- [x] React dashboard source for the seven requested workspace areas.
- [x] README and architecture, methodology, API, limitations, resume and demo documents.
- [x] Backend unit/API test suite: 9 passed.
- [x] Live local Uvicorn smoke test: `/health` returned HTTP 200.
- [x] Smoke tested market data, statistics, optimization and model-training API routes.

## Not verified or not implemented
- [ ] Frontend dependency installation and production build: npm install timed out in this environment, so build is not verified.
- [ ] Live yfinance download: not tested; depends on external network/provider access.
- [ ] Docker Compose startup: not tested.
- [ ] Ruff linting and frontend browser-level integration tests.
- [ ] Persist fitted model artifacts for inference after restart.
- [ ] Full rolling walk-forward retraining, model version registry, and background jobs.
- [ ] Historical point-in-time constituents, sector constraints, Black-Litterman, GARCH, LSTM and reinforcement learning.
- [ ] Separate gross/net performance series and detailed asset-level risk attribution.

This checklist distinguishes source implementation from execution evidence; unchecked items must not be represented as complete.
