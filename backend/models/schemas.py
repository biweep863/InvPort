"""Pydantic schemas for API request/response models."""

from typing import Literal

from pydantic import BaseModel, Field


# --- Optimization ---

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


class PortfolioMetrics(BaseModel):
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    calmar_ratio: float = 0.0
    cvar_95: float = 0.0
    beta: float = 0.0
    alpha: float = 0.0
    treynor_ratio: float = 0.0
    information_ratio: float = 0.0
    risk_contributions: list[float] = []


class OptimizeResponse(BaseModel):
    allocations: list[AllocationItem]
    portfolio_return: float
    portfolio_volatility: float
    sharpe_ratio: float
    method: str
    efficient_frontier: list[dict] | None = None
    metrics: PortfolioMetrics | None = None


# --- Simulation ---

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
    cvar_95: float = 0.0
    max_drawdown_median: float = 0.0
    max_drawdown_95: float = 0.0
    worst_case_final: float = 0.0
    best_case_final: float = 0.0


# --- Backtest ---

class BacktestRequest(BaseModel):
    tickers: list[str]
    weights: list[float]
    investment_amount: float = 10000.0


class BacktestResponse(BaseModel):
    dates: list[str]
    portfolio_values: list[float]
    benchmark_values: list[float]
    drawdown_series: list[float]
    total_return: float
    annualized_return: float
    max_drawdown: float
    max_drawdown_date: str
    best_day: float
    worst_day: float
    benchmark_total_return: float


# --- Stock Analysis ---

class StockAnalysis(BaseModel):
    ticker: str
    name: str
    current_price: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    beta: float
    high_52w: float
    low_52w: float
    price_history: list[float]  # last 60 trading days for sparkline


class StockInfo(BaseModel):
    ticker: str
    name: str
    current_price: float | None = None
