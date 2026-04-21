"""Tests for extended portfolio metrics."""

import numpy as np
import pytest

from backend.models.metrics import (
    sortino_ratio,
    max_drawdown,
    drawdown_series,
    calmar_ratio,
    cvar_expected_shortfall,
    portfolio_beta,
    portfolio_alpha,
    treynor_ratio,
    information_ratio,
    risk_contributions,
    compute_all_metrics,
)


@pytest.fixture
def daily_returns():
    """Synthetic daily returns for a portfolio."""
    np.random.seed(42)
    return np.random.normal(0.0004, 0.015, 252)


@pytest.fixture
def benchmark_returns():
    """Synthetic benchmark daily returns."""
    np.random.seed(99)
    return np.random.normal(0.0003, 0.012, 252)


class TestSortinoRatio:
    def test_returns_float(self, daily_returns):
        result = sortino_ratio(daily_returns)
        assert isinstance(result, float)

    def test_positive_for_positive_returns(self):
        # Large positive returns with some small negatives
        returns = np.array([0.01, 0.02, 0.015, -0.005, 0.01] * 50)
        result = sortino_ratio(returns, risk_free_rate=0.0)
        # With rf=0, any negative return counts as downside
        assert result >= 0

    def test_negative_for_bad_returns(self):
        returns = np.array([-0.02, -0.01, -0.015, 0.005, -0.01] * 50)
        result = sortino_ratio(returns, risk_free_rate=0.0)
        assert result < 0


class TestMaxDrawdown:
    def test_returns_float(self, daily_returns):
        result = max_drawdown(daily_returns)
        assert isinstance(result, float)

    def test_between_0_and_1(self, daily_returns):
        result = max_drawdown(daily_returns)
        assert 0 <= result <= 1

    def test_zero_for_always_positive(self):
        returns = np.array([0.01, 0.02, 0.01, 0.015, 0.01])
        result = max_drawdown(returns)
        assert result == pytest.approx(0.0, abs=1e-10)

    def test_known_drawdown(self):
        # 100 -> 110 -> 88 -> 96.8
        returns = np.array([0.10, -0.20, 0.10])
        result = max_drawdown(returns)
        # Peak is 1.10, trough is 0.88, dd = (1.10-0.88)/1.10 = 0.2
        assert result == pytest.approx(0.2, abs=0.01)


class TestDrawdownSeries:
    def test_shape(self, daily_returns):
        dd = drawdown_series(daily_returns)
        assert dd.shape == daily_returns.shape

    def test_non_negative(self, daily_returns):
        dd = drawdown_series(daily_returns)
        assert np.all(dd >= -1e-10)


class TestCalmarRatio:
    def test_returns_float(self, daily_returns):
        result = calmar_ratio(daily_returns)
        assert isinstance(result, float)

    def test_zero_when_no_drawdown(self):
        returns = np.array([0.01] * 100)
        result = calmar_ratio(returns)
        assert result == 0.0  # max drawdown is 0


class TestCVaR:
    def test_returns_float(self, daily_returns):
        result = cvar_expected_shortfall(daily_returns)
        assert isinstance(result, float)

    def test_positive(self, daily_returns):
        result = cvar_expected_shortfall(daily_returns)
        assert result >= 0

    def test_cvar_greater_than_var(self, daily_returns):
        # CVaR should be at least as large as VaR
        var_95 = -np.percentile(daily_returns, 5) * np.sqrt(252)
        cvar = cvar_expected_shortfall(daily_returns, 0.95)
        assert cvar >= var_95 - 0.01  # small tolerance


class TestBeta:
    def test_returns_float(self, daily_returns, benchmark_returns):
        result = portfolio_beta(daily_returns, benchmark_returns)
        assert isinstance(result, float)

    def test_beta_of_benchmark_is_one(self, benchmark_returns):
        result = portfolio_beta(benchmark_returns, benchmark_returns)
        assert result == pytest.approx(1.0, abs=0.01)

    def test_handles_different_lengths(self):
        p = np.random.normal(0, 0.01, 200)
        b = np.random.normal(0, 0.01, 250)
        result = portfolio_beta(p, b)
        assert isinstance(result, float)


class TestAlpha:
    def test_returns_float(self, daily_returns, benchmark_returns):
        result = portfolio_alpha(daily_returns, benchmark_returns)
        assert isinstance(result, float)


class TestTreynorRatio:
    def test_returns_float(self, daily_returns, benchmark_returns):
        result = treynor_ratio(daily_returns, benchmark_returns)
        assert isinstance(result, float)


class TestInformationRatio:
    def test_returns_float(self, daily_returns, benchmark_returns):
        result = information_ratio(daily_returns, benchmark_returns)
        assert isinstance(result, float)

    def test_zero_for_identical(self, daily_returns):
        result = information_ratio(daily_returns, daily_returns)
        assert result == pytest.approx(0.0, abs=0.01)


class TestRiskContributions:
    def test_sums_to_one(self, sample_cov_matrix):
        weights = np.array([0.4, 0.3, 0.3])
        rc = risk_contributions(weights, sample_cov_matrix)
        assert sum(rc) == pytest.approx(1.0, abs=0.01)

    def test_shape(self, sample_cov_matrix):
        weights = np.array([0.5, 0.3, 0.2])
        rc = risk_contributions(weights, sample_cov_matrix)
        assert rc.shape == (3,)

    def test_non_negative_for_long_only(self, sample_cov_matrix):
        weights = np.array([0.4, 0.3, 0.3])
        rc = risk_contributions(weights, sample_cov_matrix)
        assert np.all(rc >= -0.01)


class TestComputeAllMetrics:
    def test_returns_all_keys(self, sample_cov_matrix):
        np.random.seed(42)
        daily_ret = np.random.normal(0.0004, 0.015, (252, 3))
        bench = np.random.normal(0.0003, 0.012, 252)
        weights = np.array([0.4, 0.3, 0.3])

        result = compute_all_metrics(weights, daily_ret, bench, sample_cov_matrix)
        expected_keys = {
            "sortino_ratio", "max_drawdown", "calmar_ratio", "cvar_95",
            "beta", "alpha", "treynor_ratio", "information_ratio",
            "risk_contributions",
        }
        assert set(result.keys()) == expected_keys

    def test_risk_contributions_length(self, sample_cov_matrix):
        np.random.seed(42)
        daily_ret = np.random.normal(0.0004, 0.015, (252, 3))
        bench = np.random.normal(0.0003, 0.012, 252)
        weights = np.array([0.4, 0.3, 0.3])

        result = compute_all_metrics(weights, daily_ret, bench, sample_cov_matrix)
        assert len(result["risk_contributions"]) == 3
