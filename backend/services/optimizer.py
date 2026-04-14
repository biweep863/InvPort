"""Orchestrator: combines market data fetching with portfolio optimization."""

import numpy as np

from InvPort.backend.config import RISK_PROFILES, SP500_TICKERS
from InvPort.backend.models.portfolio import (
    compute_efficient_frontier,
    markowitz_optimize,
    genetic_optimize,
    monte_carlo_simulation,
)
from InvPort.backend.models.schemas import (
    AllocationItem,
    OptimizeRequest,
    OptimizeResponse,
    SimulateRequest,
    SimulateResponse,
)
from InvPort.backend.services.market_data import (
    compute_returns,
    compute_stats,
    fetch_historical,
)


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

    responses = []
    for method_name, result in results:
        weights = result["weights"]
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

    return SimulateResponse(
        percentiles=percentiles,
        prob_loss=prob_loss,
        var_95=var_95,
        expected_final=expected_final,
        days=req.days,
    )
