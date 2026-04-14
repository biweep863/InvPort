"""Yahoo Finance data wrapper with caching."""

import numpy as np
import pandas as pd
import yfinance as yf
from cachetools import TTLCache

from InvPort.backend.config import DEFAULT_HISTORY_PERIOD, TRADING_DAYS_PER_YEAR

# Cache: max 100 entries, 1-hour TTL
_price_cache = TTLCache(maxsize=100, ttl=3600)


def fetch_historical(tickers: list[str], period: str = DEFAULT_HISTORY_PERIOD) -> pd.DataFrame:
    """Download adjusted close prices for a list of tickers."""
    cache_key = (tuple(sorted(tickers)), period)
    if cache_key in _price_cache:
        return _price_cache[cache_key]

    data = yf.download(tickers, period=period, auto_adjust=True, progress=False)

    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data[["Close"]]
        prices.columns = tickers

    prices = prices.dropna()
    _price_cache[cache_key] = prices
    return prices


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute daily log returns."""
    return np.log(prices / prices.shift(1)).dropna()


def compute_stats(returns: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Compute annualized mean returns and covariance matrix."""
    mean_returns = returns.mean().values * TRADING_DAYS_PER_YEAR
    cov_matrix = returns.cov().values * TRADING_DAYS_PER_YEAR
    return mean_returns, cov_matrix


def get_current_prices(tickers: list[str]) -> dict[str, float]:
    """Get most recent closing price for each ticker."""
    prices = fetch_historical(tickers, period="5d")
    latest = prices.iloc[-1]
    return {ticker: float(latest[ticker]) for ticker in tickers}
