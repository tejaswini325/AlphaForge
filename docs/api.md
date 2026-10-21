# API reference

FastAPI Swagger UI is available at `/docs`; OpenAPI JSON at `/openapi.json`.

- `GET /health`: process health.
- `GET /api/v1/assets`: demo symbols.
- `GET /api/v1/market-data`: query `symbols`, `start`, `periods`, `data_source`.
- `GET /api/v1/data-quality`: synthetic data quality report.
- `GET /api/v1/statistics`: volatility, mean returns, correlations and ADF summaries.
- `POST /api/v1/models/train`: run chronological model comparison.
- `GET /api/v1/models`: available estimators.
- `GET /api/v1/models/{model_id}`: model run guidance.
- `POST /api/v1/predictions`: run comparison and return Ridge test predictions.
- `POST /api/v1/portfolio/optimize`: calculate constrained weights.
- `POST /api/v1/backtests`: run and persist a backtest.
- `GET /api/v1/backtests`: latest persisted backtests.
- `GET /api/v1/backtests/{backtest_id}`: run ID guidance; persisted lookup currently uses experiment IDs.
- `GET /api/v1/experiments`: latest persisted experiments.
- `GET /api/v1/experiments/{experiment_id}`: retrieve one persisted experiment.

Long-running endpoints currently execute synchronously. Requests have Pydantic bounds on symbols, periods and parameters. Errors use FastAPI HTTP error responses.
