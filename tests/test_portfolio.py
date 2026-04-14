"""Tests for portfolio optimization algorithms."""

import numpy as np
import pytest

from InvPort.backend.models.portfolio import (
    _portfolio_performance,
    markowitz_optimize,
    genetic_optimize,
    compute_efficient_frontier,
    monte_carlo_simulation,
)


class TestPortfolioPerformance:
    def test_returns_three_values(self, equal_weights, sample_mean_returns, sample_cov_matrix):
        ret, vol, sharpe = _portfolio_performance(equal_weights, sample_mean_returns, sample_cov_matrix)
        assert isinstance(ret, float)
        assert isinstance(vol, float)
        assert isinstance(sharpe, float)

    def test_return_is_weighted_average(self, sample_mean_returns, sample_cov_matrix):
        weights = np.array([1.0, 0.0, 0.0])
        ret, _, _ = _portfolio_performance(weights, sample_mean_returns, sample_cov_matrix)
        assert ret == pytest.approx(0.15)

    def test_volatility_is_positive(self, equal_weights, sample_mean_returns, sample_cov_matrix):
        _, vol, _ = _portfolio_performance(equal_weights, sample_mean_returns, sample_cov_matrix)
        assert vol > 0

    def test_sharpe_formula(self, equal_weights, sample_mean_returns, sample_cov_matrix):
        ret, vol, sharpe = _portfolio_performance(equal_weights, sample_mean_returns, sample_cov_matrix)
        expected_sharpe = (ret - 0.05) / vol
        assert sharpe == pytest.approx(expected_sharpe)


class TestMarkowitzOptimize:
    def test_weights_sum_to_one(self, sample_mean_returns, sample_cov_matrix):
        result = markowitz_optimize(sample_mean_returns, sample_cov_matrix)
        assert sum(result["weights"]) == pytest.approx(1.0)

    def test_weights_non_negative(self, sample_mean_returns, sample_cov_matrix):
        result = markowitz_optimize(sample_mean_returns, sample_cov_matrix)
        assert all(w >= 0 for w in result["weights"])

    def test_returns_expected_keys(self, sample_mean_returns, sample_cov_matrix):
        result = markowitz_optimize(sample_mean_returns, sample_cov_matrix)
        assert set(result.keys()) == {"weights", "expected_return", "volatility", "sharpe_ratio"}

    def test_with_target_volatility(self, sample_mean_returns, sample_cov_matrix):
        target = 0.15
        result = markowitz_optimize(sample_mean_returns, sample_cov_matrix, target_volatility=target)
        assert result["volatility"] <= target + 0.01  # small tolerance

    def test_sharpe_maximization_no_target(self, sample_mean_returns, sample_cov_matrix):
        result = markowitz_optimize(sample_mean_returns, sample_cov_matrix)
        assert result["sharpe_ratio"] > 0

    def test_two_asset_portfolio(self):
        mean_ret = np.array([0.10, 0.20])
        cov = np.array([[0.01, 0.002], [0.002, 0.04]])
        result = markowitz_optimize(mean_ret, cov)
        assert len(result["weights"]) == 2
        assert sum(result["weights"]) == pytest.approx(1.0)


class TestGeneticOptimize:
    def test_weights_sum_to_one(self, sample_mean_returns, sample_cov_matrix):
        result = genetic_optimize(sample_mean_returns, sample_cov_matrix, generations=20, population_size=50)
        assert sum(result["weights"]) == pytest.approx(1.0)

    def test_weights_non_negative(self, sample_mean_returns, sample_cov_matrix):
        result = genetic_optimize(sample_mean_returns, sample_cov_matrix, generations=20, population_size=50)
        assert all(w >= 0 for w in result["weights"])

    def test_returns_expected_keys(self, sample_mean_returns, sample_cov_matrix):
        result = genetic_optimize(sample_mean_returns, sample_cov_matrix, generations=20, population_size=50)
        assert set(result.keys()) == {"weights", "expected_return", "volatility", "sharpe_ratio"}

    def test_with_target_volatility(self, sample_mean_returns, sample_cov_matrix):
        target = 0.15
        result = genetic_optimize(sample_mean_returns, sample_cov_matrix, target_volatility=target, generations=50, population_size=100)
        # Genetic algorithm may not perfectly hit target, allow wider tolerance
        assert result["volatility"] <= target + 0.05

    def test_deterministic_with_seed(self, sample_mean_returns, sample_cov_matrix):
        r1 = genetic_optimize(sample_mean_returns, sample_cov_matrix, generations=20, population_size=50)
        r2 = genetic_optimize(sample_mean_returns, sample_cov_matrix, generations=20, population_size=50)
        assert r1["weights"] == pytest.approx(r2["weights"])


class TestEfficientFrontier:
    def test_returns_list_of_dicts(self, sample_mean_returns, sample_cov_matrix):
        frontier = compute_efficient_frontier(sample_mean_returns, sample_cov_matrix, n_points=10)
        assert isinstance(frontier, list)
        assert len(frontier) > 0
        assert all(isinstance(p, dict) for p in frontier)

    def test_frontier_points_have_expected_keys(self, sample_mean_returns, sample_cov_matrix):
        frontier = compute_efficient_frontier(sample_mean_returns, sample_cov_matrix, n_points=10)
        for point in frontier:
            assert set(point.keys()) == {"expected_return", "volatility", "sharpe_ratio", "weights"}

    def test_frontier_returns_span_range(self, sample_mean_returns, sample_cov_matrix):
        frontier = compute_efficient_frontier(sample_mean_returns, sample_cov_matrix, n_points=20)
        returns = [p["expected_return"] for p in frontier]
        assert max(returns) > min(returns)

    def test_frontier_weights_valid(self, sample_mean_returns, sample_cov_matrix):
        frontier = compute_efficient_frontier(sample_mean_returns, sample_cov_matrix, n_points=10)
        for point in frontier:
            assert sum(point["weights"]) == pytest.approx(1.0, abs=1e-4)
            assert all(w >= 0 for w in point["weights"])


class TestMonteCarloSimulation:
    def test_output_shape(self, equal_weights, sample_mean_returns, sample_cov_matrix):
        values = monte_carlo_simulation(
            equal_weights, sample_mean_returns, sample_cov_matrix,
            initial_investment=10000, days=10, n_simulations=5,
        )
        assert values.shape == (5, 11)  # n_simulations x (days + 1)

    def test_initial_value(self, equal_weights, sample_mean_returns, sample_cov_matrix):
        values = monte_carlo_simulation(
            equal_weights, sample_mean_returns, sample_cov_matrix,
            initial_investment=5000, days=10, n_simulations=3,
        )
        assert all(values[:, 0] == 5000.0)

    def test_values_positive(self, equal_weights, sample_mean_returns, sample_cov_matrix):
        values = monte_carlo_simulation(
            equal_weights, sample_mean_returns, sample_cov_matrix,
            initial_investment=10000, days=50, n_simulations=10,
        )
        assert np.all(values > 0)

    def test_deterministic_with_seed(self, equal_weights, sample_mean_returns, sample_cov_matrix):
        kwargs = dict(initial_investment=10000, days=10, n_simulations=5)
        v1 = monte_carlo_simulation(equal_weights, sample_mean_returns, sample_cov_matrix, **kwargs)
        v2 = monte_carlo_simulation(equal_weights, sample_mean_returns, sample_cov_matrix, **kwargs)
        np.testing.assert_array_equal(v1, v2)
