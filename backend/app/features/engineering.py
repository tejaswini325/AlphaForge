from __future__ import annotations
import pandas as pd

def simple_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change(fill_method=None)

def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return (prices / prices.shift(1)).apply(lambda x: __import__("numpy").log(x))

def make_features(prices: pd.DataFrame, windows: tuple[int, ...] = (5, 20, 60)) -> pd.DataFrame:
    """Long-form point-in-time features. Each row at t uses prices through close t."""
    r = simple_returns(prices)
    parts = []
    for symbol in prices.columns:
        frame = pd.DataFrame(index=prices.index)
        frame["symbol"] = symbol
        frame["ret_1"] = r[symbol]
        for w in windows:
            frame[f"momentum_{w}"] = prices[symbol].pct_change(w, fill_method=None)
            frame[f"volatility_{w}"] = r[symbol].rolling(w, min_periods=w).std()
            frame[f"ma_gap_{w}"] = prices[symbol] / prices[symbol].rolling(w, min_periods=w).mean() - 1
        frame["target"] = r[symbol].shift(-1)
        parts.append(frame)
    out = pd.concat(parts).rename_axis("date").reset_index()
    return out.replace([float("inf"), float("-inf")], float("nan"))

def data_quality(prices: pd.DataFrame, failed_symbols: list[str] | None = None) -> dict:
    return {
        "assets": int(prices.shape[1]),
        "observations": int(prices.shape[0]),
        "start_date": str(prices.index.min().date()),
        "end_date": str(prices.index.max().date()),
        "missing_percent_by_asset": (prices.isna().mean() * 100).round(3).to_dict(),
        "duplicate_timestamps": int(prices.index.duplicated().sum()),
        "failed_symbols": failed_symbols or [],
        "limitations": ["Fixed universe may have survivorship bias.", "Synthetic data, if selected, is illustrative only."]
    }
