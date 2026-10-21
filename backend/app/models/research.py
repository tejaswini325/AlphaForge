from __future__ import annotations
import uuid
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

FEATURES = ["ret_1", "momentum_5", "momentum_20", "momentum_60", "volatility_5", "volatility_20", "volatility_60", "ma_gap_5", "ma_gap_20", "ma_gap_60"]

def train_compare(features: pd.DataFrame, seed: int = 42) -> dict:
    data = features.dropna(subset=["target"]).sort_values("date")
    data = data.dropna(subset=FEATURES, how="all")
    if data["date"].nunique() < 100:
        raise ValueError("At least 100 distinct dates are required for chronological model evaluation.")
    dates = sorted(data.date.unique())
    train_end, valid_end = int(len(dates)*0.6), int(len(dates)*0.8)
    train = data[data.date <= dates[train_end-1]]
    valid = data[(data.date > dates[train_end-1]) & (data.date <= dates[valid_end-1])]
    test = data[data.date > dates[valid_end-1]]
    if min(len(train), len(valid), len(test)) == 0:
        raise ValueError("Insufficient observations for train/validation/test split.")
    Xtr, ytr = train[FEATURES], train.target
    Xte, yte = test[FEATURES], test.target
    models = {
        "ridge": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=10.0)),
        "random_forest": make_pipeline(SimpleImputer(strategy="median"), RandomForestRegressor(n_estimators=100, min_samples_leaf=5, max_features=0.8, random_state=seed, n_jobs=-1)),
        "hist_gradient_boosting": make_pipeline(SimpleImputer(strategy="median"), HistGradientBoostingRegressor(max_iter=100, l2_regularization=1.0, random_state=seed))
    }
    baseline = np.zeros(len(test))
    rows = [{"model": "zero_return_baseline", "mae": float(mean_absolute_error(yte, baseline)), "rmse": float(np.sqrt(mean_squared_error(yte, baseline))), "directional_accuracy": float(np.mean((baseline > 0) == (yte.to_numpy() > 0)))}]
    predictions = {}
    for name, model in models.items():
        model.fit(Xtr, ytr)
        pred = model.predict(Xte)
        predictions[name] = {"actual": yte.tolist(), "predicted": pred.tolist(), "dates": test.date.astype(str).tolist(), "symbols": test.symbol.tolist()}
        rows.append({"model": name, "mae": float(mean_absolute_error(yte, pred)), "rmse": float(np.sqrt(mean_squared_error(yte, pred))), "directional_accuracy": float(np.mean((pred > 0) == (yte.to_numpy() > 0)))})
    # Daily cross-sectional IC for the best available non-baseline model.
    chosen = models["ridge"].predict(Xte)
    pred_frame = test[["date", "symbol", "target"]].copy()
    pred_frame["prediction"] = chosen
    ics = []
    for date, group in pred_frame.groupby("date"):
        if len(group) >= 3 and group.target.nunique() > 1 and group.prediction.nunique() > 1:
            ics.append(float(group.target.corr(group.prediction)))
    return {"model_run_id": str(uuid.uuid4()), "split": {"train_end": str(train.date.max()), "validation_end": str(valid.date.max()), "test_start": str(test.date.min()), "test_end": str(test.date.max()), "method": "chronological date split; preprocessing fitted on training only"}, "metrics": rows, "predictions": predictions, "ridge_daily_ic_mean": float(np.mean(ics)) if ics else None, "ridge_daily_ic_std": float(np.std(ics, ddof=1)) if len(ics)>1 else None, "note": "Predictive metrics are not evidence of profitability. The test set is out-of-sample relative to model fitting."}
