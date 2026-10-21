from pydantic import BaseModel, Field
from typing import Literal

class BacktestRequest(BaseModel):
    symbols: list[str] = Field(default_factory=lambda: ["ASSET_A","ASSET_B","ASSET_C","ASSET_D"], min_length=1, max_length=50)
    start: str = "2018-01-01"
    periods: int = Field(default=1200, ge=100, le=2500)
    data_source: Literal["synthetic", "yfinance"] = "synthetic"
    strategy: Literal["equal_weight","inverse_volatility","minimum_variance","mean_variance"] = "equal_weight"
    benchmark: str | None = None
    initial_capital: float = Field(default=100000, gt=0, le=1e12)
    rebalance_every: int = Field(default=21, ge=1, le=252)
    transaction_cost_bps: float = Field(default=8, ge=0, le=1000)
    slippage_bps: float = Field(default=2, ge=0, le=1000)
    max_weight: float = Field(default=0.25, gt=0, le=1)
    risk_aversion: float = Field(default=5, gt=0, le=1000)

class OptimizeRequest(BaseModel):
    symbols: list[str] = Field(default_factory=lambda: ["ASSET_A","ASSET_B","ASSET_C","ASSET_D"], min_length=1, max_length=50)
    data_source: Literal["synthetic", "yfinance"] = "synthetic"
    strategy: Literal["equal_weight","inverse_volatility","minimum_variance","mean_variance"] = "inverse_volatility"
    start: str = "2018-01-01"
    periods: int = Field(default=500, ge=100, le=2500)
    max_weight: float = Field(default=0.25, gt=0, le=1)
    risk_aversion: float = Field(default=5, gt=0, le=1000)
