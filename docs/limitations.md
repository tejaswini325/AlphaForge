# Limitations and known issues

- Default synthetic series are deterministic, but not realistic market data. Label all such charts and results accordingly.
- yfinance is a convenience source, not a guaranteed production feed. Availability, corporate-action adjustments and rate limits can change.
- Fixed-universe backtests do not remove survivorship bias.
- No delisted constituents or point-in-time universe membership is included.
- The close-to-close simulator uses prior-close return history for decisions and next interval returns for performance, but does not model next-open execution or intraday fills.
- Cost accounting is simplified; spread, market impact, taxes and minimum commissions are omitted.
- The model pipeline uses a date-based holdout, but does not yet implement full rolling walk-forward retraining or persist fitted model files.
- Validation data is reserved but not used for automated tuning. Daily IC is computed only for Ridge.
- The API does not use a background job queue. Experiment JSON persistence can grow with long prediction payloads.
- Portfolio attribution, sector constraints, Black-Litterman, cash allocation, LSTM, GARCH and reinforcement learning are not implemented.
- Frontend navigation is implemented as a single-page research workspace; not all pages have dedicated backend endpoints.
- This is not suitable for institutional trading or real-money execution.
