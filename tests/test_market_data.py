"""Tests for market data service (using synthetic data, no network calls)."""

import numpy as np
import pandas as pd
import pytest

from backend.services.market_data import compute_returns, compute_stats


class TestComputeReturns:
    def test_log_returns_shape(self, sample_prices):
        returns = compute_returns(sample_prices)
        assert returns.shape[0] == sample_prices.shape[0] - 1
        assert returns.shape[1] == sample_prices.shape[1]

    def test_log_returns_values(self):
        prices = pd.DataFrame({"A": [100.0, 110.0, 121.0]})
        returns = compute_returns(prices)
        expected = np.log(np.array([110 / 100, 121 / 110]))
        np.testing.assert_array_almost_equal(returns["A"].values, expected)

    def test_no_nans(self, sample_prices):
        returns = compute_returns(sample_prices)
        assert not returns.isna().any().any()


class TestComputeStats:
    def test_mean_returns_shape(self, sample_prices):
        returns = compute_returns(sample_prices)
        mean_ret, cov = compute_stats(returns)
        n_assets = sample_prices.shape[1]
        assert mean_ret.shape == (n_assets,)
        assert cov.shape == (n_assets, n_assets)

    def test_cov_symmetric(self, sample_prices):
        returns = compute_returns(sample_prices)
        _, cov = compute_stats(returns)
        np.testing.assert_array_almost_equal(cov, cov.T)

    def test_cov_positive_semidefinite(self, sample_prices):
        returns = compute_returns(sample_prices)
        _, cov = compute_stats(returns)
        eigenvalues = np.linalg.eigvalsh(cov)
        assert np.all(eigenvalues >= -1e-10)

    def test_annualized(self, sample_prices):
        returns = compute_returns(sample_prices)
        mean_ret, cov = compute_stats(returns)
        daily_mean = returns.mean().values
        # Should be annualized (multiplied by 252)
        np.testing.assert_array_almost_equal(mean_ret, daily_mean * 252)
