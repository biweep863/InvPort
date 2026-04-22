"""Orchestrator: combines market data fetching with portfolio optimization."""

import numpy as np

from backend.config import RISK_PROFILES, SP500_TICKERS
from backend.models.backtest import run_backtest
from backend.models.metrics import compute_all_metrics
from backend.models.portfolio import (
    compute_efficient_frontier,
    markowitz_optimize,
    genetic_optimize,
    monte_carlo_simulation,
)
from backend.models.schemas import (
    AllocationItem,
    BacktestRequest,
    BacktestResponse,
    OptimizeRequest,
    OptimizeResponse,
    PortfolioMetrics,
    SimulateRequest,
    SimulateResponse,
    StockAnalysis,
)
from backend.services.market_data import (
    compute_returns,
    compute_simple_returns,
    compute_stats,
    fetch_benchmark,
    fetch_historical,
)
from backend.config import RISK_FREE_RATE, TRADING_DAYS_PER_YEAR


def run_optimization(req: OptimizeRequest) -> OptimizeResponse | list[OptimizeResponse]:
    """Execute the full optimization pipeline."""
    prices = fetch_historical(req.tickers)
    returns = compute_returns(prices)
    mean_returns, cov_matrix = compute_stats(returns)

    target_vol = RISK_PROFILES[req.risk_profile]["target_volatility"]

    # Run optimization(s)
    if req.method == "markowitz":
        result = markowitz_optimize(mean_returns, cov_matrix, target_vol)
        results = [("markowitz", result)]
    elif req.method == "genetic":
        result = genetic_optimize(mean_returns, cov_matrix, target_vol)
        results = [("genetic", result)]
    else:
        r1 = markowitz_optimize(mean_returns, cov_matrix, target_vol)
        r2 = genetic_optimize(mean_returns, cov_matrix, target_vol)
        results = [("markowitz", r1), ("genetic", r2)]

    # Compute efficient frontier
    frontier = compute_efficient_frontier(mean_returns, cov_matrix)

    # Fetch benchmark for metrics
    benchmark_prices = fetch_benchmark()
    bench_returns = compute_simple_returns(benchmark_prices.to_frame()).values.flatten()

    # Daily simple returns for metrics computation
    simple_returns = compute_simple_returns(prices)

    # Align lengths between portfolio and benchmark returns
    daily_ret_matrix = simple_returns.values
    min_len = min(len(daily_ret_matrix), len(bench_returns))
    if min_len > 0:
        daily_ret_matrix = daily_ret_matrix[-min_len:]
        bench_returns = bench_returns[-min_len:]

    responses = []
    for method_name, result in results:
        weights = np.array(result["weights"])
        allocations = []
        for i, ticker in enumerate(req.tickers):
            allocations.append(AllocationItem(
                ticker=ticker,
                company_name=SP500_TICKERS.get(ticker, ticker),
                weight=weights[i],
                amount=round(weights[i] * req.investment_amount, 2),
                expected_return=float(mean_returns[i]),
            ))

        # Sort by weight descending
        allocations.sort(key=lambda a: a.weight, reverse=True)

        # Compute extended metrics
        extended = compute_all_metrics(
            weights, daily_ret_matrix, bench_returns, cov_matrix,
        )
        # Reorder risk_contributions to match sorted allocations
        ticker_order = [a.ticker for a in allocations]
        original_order = list(req.tickers)
        rc_raw = extended["risk_contributions"]
        rc_sorted = [rc_raw[original_order.index(t)] for t in ticker_order]

        metrics = PortfolioMetrics(
            sortino_ratio=extended["sortino_ratio"],
            max_drawdown=extended["max_drawdown"],
            calmar_ratio=extended["calmar_ratio"],
            cvar_95=extended["cvar_95"],
            beta=extended["beta"],
            alpha=extended["alpha"],
            treynor_ratio=extended["treynor_ratio"],
            information_ratio=extended["information_ratio"],
            risk_contributions=rc_sorted,
        )

        responses.append(OptimizeResponse(
            allocations=allocations,
            portfolio_return=result["expected_return"],
            portfolio_volatility=result["volatility"],
            sharpe_ratio=result["sharpe_ratio"],
            method=method_name,
            efficient_frontier=[
                {"expected_return": p["expected_return"], "volatility": p["volatility"]}
                for p in frontier
            ],
            metrics=metrics,
        ))

    return responses if len(responses) > 1 else responses[0]


def run_simulation(req: SimulateRequest) -> SimulateResponse:
    """Run Monte Carlo simulation for a given allocation."""
    prices = fetch_historical(req.tickers)
    returns = compute_returns(prices)
    mean_returns, cov_matrix = compute_stats(returns)

    weights = np.array(req.weights)
    values = monte_carlo_simulation(
        weights, mean_returns, cov_matrix,
        initial_investment=req.investment_amount,
        days=req.days,
        n_simulations=req.n_simulations,
    )

    final_values = values[:, -1]

    percentiles = {}
    for p, label in [(5, "p5"), (25, "p25"), (50, "p50"), (75, "p75"), (95, "p95")]:
        percentiles[label] = np.percentile(values, p, axis=0).tolist()

    prob_loss = float(np.mean(final_values < req.investment_amount))
    var_95 = float(req.investment_amount - np.percentile(final_values, 5))
    expected_final = float(np.mean(final_values))

    # Extended simulation metrics
    # CVaR: mean loss in worst 5% of outcomes
    var_threshold = np.percentile(final_values, 5)
    tail = final_values[final_values <= var_threshold]
    cvar_95 = float(req.investment_amount - np.mean(tail)) if len(tail) > 0 else 0.0

    # Max drawdown per simulation
    sim_drawdowns = []
    for sim in range(req.n_simulations):
        path = values[sim, :]
        peak = np.maximum.accumulate(path)
        dd = (peak - path) / peak
        sim_drawdowns.append(float(np.max(dd)))
    sim_drawdowns = np.array(sim_drawdowns)

    return SimulateResponse(
        percentiles=percentiles,
        prob_loss=prob_loss,
        var_95=var_95,
        expected_final=expected_final,
        days=req.days,
        cvar_95=round(cvar_95, 2),
        max_drawdown_median=round(float(np.median(sim_drawdowns)), 4),
        max_drawdown_95=round(float(np.percentile(sim_drawdowns, 95)), 4),
        worst_case_final=round(float(np.percentile(final_values, 1)), 2),
        best_case_final=round(float(np.percentile(final_values, 99)), 2),
    )


def run_backtest_service(req: BacktestRequest) -> BacktestResponse:
    """Run historical backtest for a portfolio."""
    prices = fetch_historical(req.tickers)
    benchmark_prices = fetch_benchmark()
    weights = np.array(req.weights)

    result = run_backtest(weights, prices, benchmark_prices, req.investment_amount)
    return BacktestResponse(**result)


def analyze_stocks(tickers: list[str]) -> list[StockAnalysis]:
    """Compute individual stock analysis for a list of tickers."""
    from backend.models.metrics import max_drawdown, portfolio_beta

    prices = fetch_historical(tickers)
    benchmark_prices = fetch_benchmark()
    bench_returns = benchmark_prices.pct_change().dropna().values

    results = []
    for ticker in tickers:
        if ticker not in prices.columns:
            continue
        stock_prices = prices[ticker]
        stock_returns = stock_prices.pct_change().dropna().values

        ann_return = float(np.mean(stock_returns) * TRADING_DAYS_PER_YEAR)
        ann_vol = float(np.std(stock_returns, ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR))
        sharpe = (ann_return - RISK_FREE_RATE) / ann_vol if ann_vol > 1e-10 else 0.0
        mdd = max_drawdown(stock_returns)
        beta = portfolio_beta(stock_returns, bench_returns)

        # 52-week high/low (last 252 trading days)
        recent = stock_prices.iloc[-252:] if len(stock_prices) >= 252 else stock_prices
        high_52w = float(recent.max())
        low_52w = float(recent.min())
        current_price = float(stock_prices.iloc[-1])

        # Last 60 days for sparkline
        spark = stock_prices.iloc[-60:].tolist()

        results.append(StockAnalysis(
            ticker=ticker,
            name=SP500_TICKERS.get(ticker, ticker),
            current_price=round(current_price, 2),
            annualized_return=round(ann_return, 4),
            annualized_volatility=round(ann_vol, 4),
            sharpe_ratio=round(sharpe, 4),
            max_drawdown=round(mdd, 4),
            beta=round(beta, 4),
            high_52w=round(high_52w, 2),
            low_52w=round(low_52w, 2),
            price_history=spark,
        ))

    return results
