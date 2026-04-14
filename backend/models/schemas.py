"""Pydantic schemas for API request/response models."""

from typing import Literal

from pydantic import BaseModel, Field


class OptimizeRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=2, max_length=15)
    risk_profile: Literal["bajo", "medio", "alto"]
    investment_amount: float = 10000.0
    method: Literal["markowitz", "genetic", "both"] = "markowitz"


class AllocationItem(BaseModel):
    ticker: str
    company_name: str
    weight: float
    amount: float
    expected_return: float


class OptimizeResponse(BaseModel):
    allocations: list[AllocationItem]
    portfolio_return: float
    portfolio_volatility: float
    sharpe_ratio: float
    method: str
    efficient_frontier: list[dict] | None = None


class SimulateRequest(BaseModel):
    tickers: list[str]
    weights: list[float]
    investment_amount: float = 10000.0
    days: int = 252
    n_simulations: int = 1000


class SimulateResponse(BaseModel):
    percentiles: dict[str, list[float]]  # "p5", "p25", "p50", "p75", "p95"
    prob_loss: float
    var_95: float
    expected_final: float
    days: int


class StockInfo(BaseModel):
    ticker: str
    name: str
    current_price: float | None = None
