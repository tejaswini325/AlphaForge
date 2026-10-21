from __future__ import annotations
import logging
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.data.providers import synthetic_prices, download_yfinance
from app.features.engineering import make_features, data_quality
from app.analytics.statistics import statistics_report
from app.models.research import train_compare
from app.optimization.portfolio import optimize_weights
from app.backtesting.engine import run_backtest
from app.schemas import BacktestRequest, OptimizeRequest
from app.database.db import Base, engine, SessionLocal
from app.database.models import Experiment

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("alphaforge")
app = FastAPI(title="AlphaForge API", version="1.0.0", description="Research-grade educational quantitative analytics. Not investment advice.")
app.add_middleware(CORSMiddleware, allow_origins=list(settings.frontend_origins), allow_credentials=False, allow_methods=["GET","POST"], allow_headers=["*"])
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    logger.exception("Database initialization failed; API continues without persistence.")

def load_prices(symbols, source="synthetic", start="2018-01-01", periods=1200):
    if len(symbols) > settings.max_assets:
        raise ValueError(f"Maximum asset count is {settings.max_assets}.")
    if source == "synthetic":
        return synthetic_prices(symbols, start=start, periods=periods), []
    prices, failed = download_yfinance(symbols, start=start, end=None)
    if prices.empty:
        raise ValueError("Provider returned no data.")
    return prices, failed

def save_experiment(kind, payload):
    try:
        with SessionLocal() as session:
            row = Experiment(kind=kind, payload=payload)
            session.add(row); session.commit(); session.refresh(row)
            return row.id
    except Exception:
        logger.exception("Could not persist experiment")
        return None

@app.get("/health")
def health():
    return {"status":"ok","service":"AlphaForge API","version":"1.0.0"}

@app.get("/api/v1/assets")
def assets():
    return {"assets":["ASSET_A","ASSET_B","ASSET_C","ASSET_D"],"note":"Synthetic demo symbols are not real securities. Supply real tickers for yfinance."}

@app.get("/api/v1/market-data")
def market_data(symbols: str = "ASSET_A,ASSET_B,ASSET_C,ASSET_D", start: str = "2018-01-01", periods: int = 500, data_source: str = "synthetic"):
    try:
        prices, failed = load_prices([s.strip() for s in symbols.split(",") if s.strip()], data_source, start, periods)
        return {"data_source":data_source,"quality":data_quality(prices, failed),"prices":[{"date":str(d.date()),**{k:(None if v != v else float(v)) for k,v in row.items()}} for d,row in prices.tail(500).iterrows()]}
    except Exception as exc:
        raise HTTPException(400, detail=str(exc))

@app.get("/api/v1/data-quality")
def quality(symbols: str = "ASSET_A,ASSET_B,ASSET_C,ASSET_D", start: str = "2018-01-01", periods: int = 500):
    try:
        p,_ = load_prices([s.strip() for s in symbols.split(",")], "synthetic", start, periods)
        return data_quality(p)
    except Exception as exc: raise HTTPException(400, detail=str(exc))

@app.get("/api/v1/statistics")
def statistics(symbols: str = "ASSET_A,ASSET_B,ASSET_C,ASSET_D", start: str = "2018-01-01", periods: int = 500):
    try:
        p,_ = load_prices([s.strip() for s in symbols.split(",")], "synthetic", start, periods)
        return statistics_report(p)
    except Exception as exc: raise HTTPException(400, detail=str(exc))

@app.post("/api/v1/models/train")
def train(request: OptimizeRequest):
    try:
        prices,_ = load_prices(request.symbols, request.data_source, request.start, request.periods)
        result = train_compare(make_features(prices))
        result["experiment_id"] = save_experiment("model_training", result)
        return result
    except Exception as exc: raise HTTPException(400, detail=str(exc))

@app.get("/api/v1/models")
def models():
    return {"models":["zero_return_baseline","ridge","random_forest","hist_gradient_boosting"],"note":"Models are trained on demand; only metadata is persisted in the current implementation."}

@app.get("/api/v1/models/{model_id}")
def model_detail(model_id: str):
    return {"model_id":model_id,"status":"Use POST /api/v1/models/train to create a new evaluation run."}

@app.post("/api/v1/predictions")
def predictions(request: OptimizeRequest):
    try:
        p,_ = load_prices(request.symbols, request.data_source, request.start, request.periods)
        result = train_compare(make_features(p))
        return {"model_run_id":result["model_run_id"],"predictions":result["predictions"].get("ridge",{}),"metrics":result["metrics"]}
    except Exception as exc: raise HTTPException(400, detail=str(exc))

@app.post("/api/v1/portfolio/optimize")
def optimize(request: OptimizeRequest):
    try:
        prices,_ = load_prices(request.symbols, request.data_source, request.start, request.periods)
        r = prices.pct_change(fill_method=None).dropna()
        result = optimize_weights(r, request.strategy, request.max_weight, request.risk_aversion)
        result["experiment_id"] = save_experiment("optimization", result)
        return result
    except Exception as exc: raise HTTPException(400, detail=str(exc))

@app.post("/api/v1/backtests")
def backtest(request: BacktestRequest):
    try:
        prices, failed = load_prices(request.symbols, request.data_source, request.start, request.periods)
        result = run_backtest(prices, request.strategy, request.benchmark, request.initial_capital, request.rebalance_every, request.transaction_cost_bps, request.slippage_bps, request.max_weight, request.risk_aversion)
        result["failed_symbols"] = failed
        result["backtest_id"] = str(uuid.uuid4())
        result["data_source"] = request.data_source
        result["experiment_id"] = save_experiment("backtest", result)
        return result
    except Exception as exc:
        logger.exception("Backtest failed")
        raise HTTPException(400, detail=str(exc))

@app.get("/api/v1/backtests")
def backtests():
    try:
        with SessionLocal() as session:
            rows = session.query(Experiment).filter(Experiment.kind=="backtest").order_by(Experiment.id.desc()).limit(50).all()
            return {"items":[{"id":x.id,"created_at":x.created_at.isoformat(),"result":x.payload} for x in rows]}
    except Exception as exc: raise HTTPException(503, detail="Experiment persistence unavailable.")

@app.get("/api/v1/backtests/{backtest_id}")
def backtest_detail(backtest_id: str):
    return {"backtest_id":backtest_id,"note":"In-memory run IDs are not retrievable after restart; use GET /api/v1/backtests for persisted runs."}

@app.get("/api/v1/experiments")
def experiments():
    try:
        with SessionLocal() as session:
            rows = session.query(Experiment).order_by(Experiment.id.desc()).limit(100).all()
            return {"items":[{"id":x.id,"kind":x.kind,"created_at":x.created_at.isoformat(),"payload":x.payload} for x in rows]}
    except Exception: return {"items":[],"persistence":"unavailable"}

@app.get("/api/v1/experiments/{experiment_id}")
def experiment_detail(experiment_id: int):
    try:
        with SessionLocal() as session:
            row = session.get(Experiment, experiment_id)
            if not row: raise HTTPException(404, "Experiment not found")
            return {"id":row.id,"kind":row.kind,"created_at":row.created_at.isoformat(),"payload":row.payload}
    except HTTPException: raise
    except Exception: raise HTTPException(503, "Experiment persistence unavailable")
