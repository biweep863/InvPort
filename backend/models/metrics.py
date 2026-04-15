"""Extended portfolio metrics: Sortino, drawdown, CVaR, Beta, Alpha, etc."""

import numpy as np

from InvPort.backend.config import RISK_FREE_RATE, TRADING_DAYS_PER_YEAR


def sortino_ratio(portfolio_returns: np.ndarray, risk_free_rate: float = RISK_FREE_RATE) -> float:
    """Sortino ratio: like Sharpe but only penalizes downside volatility."""
    daily_rf = risk_free_rate / TRADING_DAYS_PER_YEAR
    excess = portfolio_returns - daily_rf
    downside = portfolio_returns[portfolio_returns < daily_rf]
    if len(downside) < 2:
        return 0.0
    downside_std = np.std(downside, ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)
    ann_return = np.mean(portfolio_returns) * TRADING_DAYS_PER_YEAR
    if downside_std < 1e-10:
        return 0.0
    return (ann_return - risk_free_rate) / downside_std


def max_drawdown(portfolio_returns: np.ndarray) -> float:
    """Maximum peak-to-trough drawdown from daily returns."""
    cumulative = np.cumprod(1 + portfolio_returns)
    peak = np.maximum.accumulate(cumulative)
    drawdowns = (peak - cumulative) / peak
    return float(np.max(drawdowns)) if len(drawdowns) > 0 else 0.0


def drawdown_series(portfolio_returns: np.ndarray) -> np.ndarray:
    """Full drawdown time series from daily returns."""
    cumulative = np.cumprod(1 + portfolio_returns)
    peak = np.maximum.accumulate(cumulative)
    return (peak - cumulative) / peak


def calmar_ratio(portfolio_returns: np.ndarray, risk_free_rate: float = RISK_FREE_RATE) -> float:
    """Calmar ratio: annualized return / max drawdown."""
    mdd = max_drawdown(portfolio_returns)
    if mdd < 1e-10:
        return 0.0
    ann_return = np.mean(portfolio_returns) * TRADING_DAYS_PER_YEAR
    return (ann_return - risk_free_rate) / mdd


def cvar_expected_shortfall(portfolio_returns: np.ndarray, confidence: float = 0.95) -> float:
    """Conditional VaR (Expected Shortfall): mean loss beyond VaR threshold."""
    var_threshold = np.percentile(portfolio_returns, (1 - confidence) * 100)
    tail_losses = portfolio_returns[portfolio_returns <= var_threshold]
    if len(tail_losses) == 0:
        return 0.0
    return float(-np.mean(tail_losses) * np.sqrt(TRADING_DAYS_PER_YEAR))


def portfolio_beta(portfolio_returns: np.ndarray, benchmark_returns: np.ndarray) -> float:
    """Beta: sensitivity of portfolio to market movements."""
    if len(portfolio_returns) != len(benchmark_returns):
        min_len = min(len(portfolio_returns), len(benchmark_returns))
        portfolio_returns = portfolio_returns[-min_len:]
        benchmark_returns = benchmark_returns[-min_len:]
    cov = np.cov(portfolio_returns, benchmark_returns)
    var_benchmark = cov[1, 1]
    if var_benchmark < 1e-10:
        return 0.0
    return float(cov[0, 1] / var_benchmark)


def portfolio_alpha(
    portfolio_returns: np.ndarray,
    benchmark_returns: np.ndarray,
    risk_free_rate: float = RISK_FREE_RATE,
) -> float:
    """Jensen's Alpha: excess return above what CAPM predicts."""
    beta = portfolio_beta(portfolio_returns, benchmark_returns)
    ann_portfolio = np.mean(portfolio_returns) * TRADING_DAYS_PER_YEAR
    ann_benchmark = np.mean(benchmark_returns) * TRADING_DAYS_PER_YEAR
    return ann_portfolio - (risk_free_rate + beta * (ann_benchmark - risk_free_rate))


def treynor_ratio(
    portfolio_returns: np.ndarray,
    benchmark_returns: np.ndarray,
    risk_free_rate: float = RISK_FREE_RATE,
) -> float:
    """Treynor ratio: excess return per unit of systematic risk (beta)."""
    beta = portfolio_beta(portfolio_returns, benchmark_returns)
    if abs(beta) < 1e-10:
        return 0.0
    ann_return = np.mean(portfolio_returns) * TRADING_DAYS_PER_YEAR
    return (ann_return - risk_free_rate) / beta


def information_ratio(portfolio_returns: np.ndarray, benchmark_returns: np.ndarray) -> float:
    """Information ratio: active return / tracking error."""
    if len(portfolio_returns) != len(benchmark_returns):
        min_len = min(len(portfolio_returns), len(benchmark_returns))
        portfolio_returns = portfolio_returns[-min_len:]
        benchmark_returns = benchmark_returns[-min_len:]
    active = portfolio_returns - benchmark_returns
    tracking_error = np.std(active, ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)
    if tracking_error < 1e-10:
        return 0.0
    ann_active = np.mean(active) * TRADING_DAYS_PER_YEAR
    return ann_active / tracking_error


def risk_contributions(weights: np.ndarray, cov_matrix: np.ndarray) -> np.ndarray:
    """Each asset's contribution to total portfolio variance (sums to 1)."""
    port_var = weights @ cov_matrix @ weights
    if port_var < 1e-10:
        return np.zeros(len(weights))
    marginal = cov_matrix @ weights
    contributions = weights * marginal / port_var
    return contributions


def compute_all_metrics(
    weights: np.ndarray,
    daily_returns: np.ndarray,
    benchmark_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float = RISK_FREE_RATE,
) -> dict:
    """Compute all extended metrics for a portfolio."""
    port_returns = daily_returns @ weights

    return {
        "sortino_ratio": round(sortino_ratio(port_returns, risk_free_rate), 4),
        "max_drawdown": round(max_drawdown(port_returns), 4),
        "calmar_ratio": round(calmar_ratio(port_returns, risk_free_rate), 4),
        "cvar_95": round(cvar_expected_shortfall(port_returns, 0.95), 4),
        "beta": round(portfolio_beta(port_returns, benchmark_returns), 4),
        "alpha": round(portfolio_alpha(port_returns, benchmark_returns, risk_free_rate), 4),
        "treynor_ratio": round(treynor_ratio(port_returns, benchmark_returns, risk_free_rate), 4),
        "information_ratio": round(information_ratio(port_returns, benchmark_returns), 4),
        "risk_contributions": risk_contributions(weights, cov_matrix).tolist(),
    }
