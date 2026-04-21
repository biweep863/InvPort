"""Historical backtesting: how would the portfolio have performed."""

import numpy as np
import pandas as pd

from backend.models.metrics import drawdown_series


def run_backtest(
    weights: np.ndarray,
    prices: pd.DataFrame,
    benchmark_prices: pd.Series,
    initial_investment: float = 10000.0,
) -> dict:
    """
    Backtest a portfolio using historical prices.

    Returns portfolio value series, benchmark comparison, drawdown, and summary stats.
    """
    # Daily simple returns
    daily_returns = prices.pct_change().dropna()
    portfolio_returns = daily_returns.values @ weights

    # Portfolio cumulative value
    cumulative = np.cumprod(1 + portfolio_returns)
    portfolio_values = initial_investment * cumulative

    # Benchmark cumulative value (normalized to same starting investment)
    bench_returns = benchmark_prices.pct_change().dropna()
    # Align dates
    common_dates = daily_returns.index.intersection(bench_returns.index)
    bench_returns_aligned = bench_returns.loc[common_dates].values
    portfolio_returns_aligned = pd.Series(portfolio_returns, index=daily_returns.index).loc[common_dates].values

    bench_cumulative = np.cumprod(1 + bench_returns_aligned)
    benchmark_values = initial_investment * bench_cumulative

    portfolio_values_aligned = initial_investment * np.cumprod(1 + portfolio_returns_aligned)

    # Drawdown series
    dd = drawdown_series(portfolio_returns_aligned)

    # Summary stats
    total_return = float(portfolio_values_aligned[-1] / initial_investment - 1)
    n_years = len(common_dates) / 252
    ann_return = float((1 + total_return) ** (1 / n_years) - 1) if n_years > 0 else 0.0
    mdd = float(np.max(dd))

    # Best and worst days
    best_day = float(np.max(portfolio_returns_aligned))
    worst_day = float(np.min(portfolio_returns_aligned))

    # Max drawdown date
    mdd_idx = int(np.argmax(dd))
    dates_list = [d.strftime("%Y-%m-%d") for d in common_dates]

    # Benchmark total return
    bench_total_return = float(benchmark_values[-1] / initial_investment - 1)

    return {
        "dates": dates_list,
        "portfolio_values": portfolio_values_aligned.tolist(),
        "benchmark_values": benchmark_values.tolist(),
        "drawdown_series": dd.tolist(),
        "total_return": round(total_return, 4),
        "annualized_return": round(ann_return, 4),
        "max_drawdown": round(mdd, 4),
        "max_drawdown_date": dates_list[mdd_idx] if mdd_idx < len(dates_list) else "",
        "best_day": round(best_day, 4),
        "worst_day": round(worst_day, 4),
        "benchmark_total_return": round(bench_total_return, 4),
    }
