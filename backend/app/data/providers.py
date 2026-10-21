from __future__ import annotations
import numpy as np
import pandas as pd

class DataProviderError(RuntimeError):
    pass

def synthetic_prices(symbols: list[str], start: str = "2018-01-01", periods: int = 1500, seed: int = 7) -> pd.DataFrame:
    """Deterministic illustrative prices; never represent these as real market data."""
    if not symbols:
        raise ValueError("At least one symbol is required.")
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(start=start, periods=periods)
    result = {}
    for i, symbol in enumerate(symbols):
        market = rng.normal(0.00025, 0.009, len(dates))
        idio = rng.normal(0.00005 * (i % 4), 0.006 + (i % 5) * 0.001, len(dates))
        returns = np.clip(market + idio, -0.15, 0.15)
        result[symbol] = 100 * np.cumprod(1 + returns)
    return pd.DataFrame(result, index=dates).rename_axis("date")

def download_yfinance(symbols: list[str], start: str, end: str | None = None) -> tuple[pd.DataFrame, list[str]]:
    """Download adjusted close prices. Requires yfinance and network access."""
    try:
        import yfinance as yf
    except ImportError as exc:
        raise DataProviderError("yfinance is not installed. Install backend requirements or use synthetic demo data.") from exc
    if not symbols:
        raise ValueError("At least one symbol is required.")
    raw = yf.download(symbols, start=start, end=end, auto_adjust=True, progress=False, group_by="column", threads=False)
    if raw is None or raw.empty:
        raise DataProviderError("The market data provider returned no observations.")
    if isinstance(raw.columns, pd.MultiIndex):
        field = "Close" if "Close" in raw.columns.get_level_values(0) else raw.columns.get_level_values(0)[0]
        prices = raw[field]
    else:
        prices = raw[["Close"]].rename(columns={"Close": symbols[0]})
    failed = [s for s in symbols if s not in prices.columns or prices[s].dropna().empty]
    prices = prices.dropna(how="all").sort_index()
    prices.index = pd.to_datetime(prices.index).tz_localize(None)
    return validate_prices(prices), failed

def validate_prices(prices: pd.DataFrame) -> pd.DataFrame:
    if prices.empty:
        raise ValueError("Price data is empty.")
    clean = prices.copy()
    clean.index = pd.to_datetime(clean.index)
    clean = clean[~clean.index.duplicated(keep="last")].sort_index()
    clean = clean.apply(pd.to_numeric, errors="coerce")
    clean = clean.where(np.isfinite(clean) & (clean > 0))
    clean = clean.dropna(axis=1, how="all")
    if clean.empty:
        raise ValueError("No valid positive prices remain after validation.")
    return clean
