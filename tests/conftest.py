"""Shared fixtures for InvPort tests."""

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_tickers():
    return ["AAPL", "MSFT", "GOOGL"]


@pytest.fixture
def sample_mean_returns():
    """Annualized mean returns for 3 assets."""
    return np.array([0.15, 0.12, 0.18])


@pytest.fixture
def sample_cov_matrix():
    """Annualized covariance matrix for 3 assets (positive-definite)."""
    return np.array([
        [0.04, 0.006, 0.008],
        [0.006, 0.03, 0.005],
        [0.008, 0.005, 0.05],
    ])


@pytest.fixture
def equal_weights():
    return np.array([1 / 3, 1 / 3, 1 / 3])


@pytest.fixture
def sample_prices(sample_tickers):
    """Synthetic daily price DataFrame (~252 days)."""
    np.random.seed(42)
    dates = pd.bdate_range("2023-01-01", periods=252)
    data = {}
    for i, ticker in enumerate(sample_tickers):
        base = 100 + i * 50
        returns = np.random.normal(0.0004, 0.015, len(dates))
        prices = base * np.cumprod(1 + returns)
        data[ticker] = prices
    return pd.DataFrame(data, index=dates)
