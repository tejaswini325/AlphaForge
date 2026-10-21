# Architecture

```mermaid
flowchart TB
  Browser[React / TypeScript / Plotly] --> REST[FastAPI + Pydantic]
  REST --> Provider[Market data provider abstraction]
  Provider --> Validate[Validation and quality report]
  Validate --> Features[Point-in-time feature engineering]
  Features --> Models[Chronological sklearn evaluation]
  Validate --> Statistics[Statistics and ADF]
  Validate --> Optimizer[Portfolio allocation]
  Optimizer --> Backtest[Cost-aware backtesting]
  Models --> Store[SQLAlchemy experiment repository]
  Backtest --> Store
  REST --> Store
  Store --> DB[(SQLite local / PostgreSQL Compose)]
```

HTTP routes validate inputs and orchestrate services. Feature, model, optimizer, metric, and backtest functions are separate modules. The database stores experiment payloads; large model artifacts are not currently persisted. The yfinance provider is optional at runtime and synthetic data is deterministic for repeatable offline demonstrations.
