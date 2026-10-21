import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.features.engineering import simple_returns, make_features, data_quality
from app.analytics.statistics import performance_metrics
from app.optimization.portfolio import optimize_weights
from app.backtesting.engine import run_backtest
from app.data.providers import validate_prices, synthetic_prices

client = TestClient(app)

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_return_calculation():
    p = pd.DataFrame({"A":[100,110,99]})
    assert np.allclose(simple_returns(p).A.dropna(), [0.1,-0.1])

def test_validation_deduplicates_and_rejects_invalid():
    p = pd.DataFrame({"A":[100,101,-3]}, index=pd.to_datetime(["2020-01-01","2020-01-02","2020-01-02"]))
    out = validate_prices(p)
    assert len(out) == 2 and out.iloc[-1,0] != out.iloc[-1,0]

def test_features_target_is_next_day_return():
    p = pd.DataFrame({"A":np.arange(100,160,dtype=float)}, index=pd.bdate_range("2020-01-01", periods=60))
    f = make_features(p, windows=(5,20))
    row = f[(f.symbol=="A") & (f.date==p.index[30])].iloc[0]
    assert row.target == pytest.approx(p.iloc[31,0]/p.iloc[30,0]-1)

def test_optimizer_weights_constraints():
    p = synthetic_prices(["A","B","C","D"], periods=200)
    out = optimize_weights(p.pct_change().dropna(), "inverse_volatility", max_weight=0.4)
    w = np.array(list(out["weights"].values()))
    assert np.isclose(w.sum(),1) and (w >= 0).all() and w.max() <= 0.40001

def test_infeasible_optimizer():
    with pytest.raises(ValueError):
        optimize_weights(pd.DataFrame(np.random.default_rng(2).normal(0,0.01,(100,3)),columns=list("ABC")), max_weight=0.2)

def test_metrics_zero_variance_safe():
    m = performance_metrics(pd.Series([0.0]*20))
    assert m["sharpe_ratio"] == 0 and m["max_drawdown"] == 0

def test_backtest_costs_and_series():
    p = synthetic_prices(["A","B","C","D"], periods=250)
    no_cost = run_backtest(p, transaction_cost_bps=0, slippage_bps=0)
    cost = run_backtest(p, transaction_cost_bps=10, slippage_bps=5)
    assert len(cost["series"]) == len(p)-1
    assert cost["metrics"]["cumulative_return"] <= no_cost["metrics"]["cumulative_return"] + 1e-9

def test_api_backtest():
    r = client.post("/api/v1/backtests", json={"symbols":["A","B","C","D"],"periods":180,"data_source":"synthetic"})
    assert r.status_code == 200
    assert "metrics" in r.json()
