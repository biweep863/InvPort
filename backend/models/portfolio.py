"""Portfolio optimization models: Markowitz, Genetic Algorithm, Monte Carlo."""

import numpy as np
from scipy.optimize import minimize

from InvPort.backend.config import RISK_FREE_RATE, TRADING_DAYS_PER_YEAR


# ---------------------------------------------------------------------------
# Markowitz Mean-Variance Optimization
# ---------------------------------------------------------------------------

def _portfolio_performance(weights: np.ndarray, mean_returns: np.ndarray, cov_matrix: np.ndarray):
    """Return (expected_return, volatility, sharpe_ratio) for a given weight vector."""
    ret = np.dot(weights, mean_returns)
    vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    sharpe = (ret - RISK_FREE_RATE) / vol if vol > 0 else 0.0
    return ret, vol, sharpe


def markowitz_optimize(
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    target_volatility: float | None = None,
) -> dict:
    """
    Find the optimal portfolio using Markowitz mean-variance optimization.

    If target_volatility is None, maximizes the Sharpe ratio.
    If target_volatility is given, maximizes return subject to vol <= target.
    """
    n = len(mean_returns)
    initial_weights = np.ones(n) / n
    bounds = tuple((0.0, 1.0) for _ in range(n))
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

    if target_volatility is not None:
        # Maximize return subject to volatility constraint
        constraints.append({
            "type": "ineq",
            "fun": lambda w: target_volatility - np.sqrt(np.dot(w.T, np.dot(cov_matrix, w))),
        })

        def objective(w):
            return -np.dot(w, mean_returns)
    else:
        # Maximize Sharpe ratio
        def objective(w):
            ret, vol, _ = _portfolio_performance(w, mean_returns, cov_matrix)
            return -(ret - RISK_FREE_RATE) / vol if vol > 1e-10 else 0.0

    result = minimize(
        objective,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-12},
    )

    weights = result.x
    # Clip tiny negatives from numerical noise
    weights = np.maximum(weights, 0.0)
    weights /= weights.sum()

    ret, vol, sharpe = _portfolio_performance(weights, mean_returns, cov_matrix)

    return {
        "weights": weights.tolist(),
        "expected_return": float(ret),
        "volatility": float(vol),
        "sharpe_ratio": float(sharpe),
    }


# ---------------------------------------------------------------------------
# Genetic Algorithm Optimization
# ---------------------------------------------------------------------------

def genetic_optimize(
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    target_volatility: float | None = None,
    generations: int = 150,
    population_size: int = 300,
) -> dict:
    """Find optimal portfolio using a simple genetic algorithm."""
    n = len(mean_returns)
    rng = np.random.default_rng(42)

    def _random_weights():
        w = rng.random(n)
        return w / w.sum()

    def _fitness(w):
        ret, vol, sharpe = _portfolio_performance(w, mean_returns, cov_matrix)
        if target_volatility is not None:
            penalty = max(0, vol - target_volatility) * 10
            return ret - penalty
        return sharpe

    # Initialize population
    population = np.array([_random_weights() for _ in range(population_size)])
    fitness_scores = np.array([_fitness(w) for w in population])

    for _ in range(generations):
        # Selection: tournament
        parents = []
        for _ in range(population_size):
            i, j = rng.integers(0, population_size, size=2)
            parents.append(population[i] if fitness_scores[i] > fitness_scores[j] else population[j])
        parents = np.array(parents)

        # Crossover: uniform
        children = []
        for k in range(0, population_size, 2):
            p1, p2 = parents[k], parents[min(k + 1, population_size - 1)]
            mask = rng.random(n) < 0.5
            c1 = np.where(mask, p1, p2)
            c2 = np.where(mask, p2, p1)
            children.extend([c1, c2])
        children = np.array(children[:population_size])

        # Mutation
        for k in range(population_size):
            if rng.random() < 0.3:
                idx = rng.integers(0, n)
                children[k][idx] += rng.normal(0, 0.05)
                children[k] = np.maximum(children[k], 0.0)
                children[k] /= children[k].sum()

        # Normalize
        for k in range(population_size):
            children[k] = np.maximum(children[k], 0.0)
            s = children[k].sum()
            if s > 0:
                children[k] /= s
            else:
                children[k] = np.ones(n) / n

        population = children
        fitness_scores = np.array([_fitness(w) for w in population])

    best_idx = np.argmax(fitness_scores)
    weights = population[best_idx]
    weights = np.maximum(weights, 0.0)
    weights /= weights.sum()

    ret, vol, sharpe = _portfolio_performance(weights, mean_returns, cov_matrix)

    return {
        "weights": weights.tolist(),
        "expected_return": float(ret),
        "volatility": float(vol),
        "sharpe_ratio": float(sharpe),
    }


# ---------------------------------------------------------------------------
# Efficient Frontier
# ---------------------------------------------------------------------------

def compute_efficient_frontier(
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    n_points: int = 50,
) -> list[dict]:
    """Compute points along the efficient frontier."""
    n = len(mean_returns)
    bounds = tuple((0.0, 1.0) for _ in range(n))
    constraints_base = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

    # Range of target returns
    min_ret = float(np.min(mean_returns))
    max_ret = float(np.max(mean_returns))
    target_returns = np.linspace(min_ret, max_ret, n_points)

    frontier = []
    for target in target_returns:
        constraints = constraints_base + [
            {"type": "eq", "fun": lambda w, t=target: np.dot(w, mean_returns) - t}
        ]

        def min_vol(w):
            return np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))

        result = minimize(
            min_vol,
            np.ones(n) / n,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 500},
        )

        if result.success:
            w = np.maximum(result.x, 0.0)
            w /= w.sum()
            ret, vol, sharpe = _portfolio_performance(w, mean_returns, cov_matrix)
            frontier.append({
                "expected_return": float(ret),
                "volatility": float(vol),
                "sharpe_ratio": float(sharpe),
                "weights": w.tolist(),
            })

    return frontier


# ---------------------------------------------------------------------------
# Monte Carlo Simulation
# ---------------------------------------------------------------------------

def monte_carlo_simulation(
    weights: np.ndarray,
    mean_returns: np.ndarray,
    cov_matrix: np.ndarray,
    initial_investment: float = 10000.0,
    days: int = 252,
    n_simulations: int = 1000,
) -> np.ndarray:
    """
    Run Monte Carlo simulation of portfolio value over time.
    Returns array of shape (n_simulations, days+1) with portfolio values.
    """
    weights = np.array(weights)
    rng = np.random.default_rng(42)

    # Daily parameters
    daily_mean = mean_returns / TRADING_DAYS_PER_YEAR
    daily_cov = cov_matrix / TRADING_DAYS_PER_YEAR

    # Cholesky decomposition for correlated returns
    L = np.linalg.cholesky(daily_cov + np.eye(len(weights)) * 1e-10)

    portfolio_values = np.zeros((n_simulations, days + 1))
    portfolio_values[:, 0] = initial_investment

    for sim in range(n_simulations):
        value = initial_investment
        for day in range(1, days + 1):
            z = rng.standard_normal(len(weights))
            daily_returns = daily_mean + L @ z
            portfolio_return = np.dot(weights, daily_returns)
            value *= (1 + portfolio_return)
            portfolio_values[sim, day] = value

    return portfolio_values
