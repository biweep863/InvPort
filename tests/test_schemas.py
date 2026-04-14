"""Tests for Pydantic schemas validation."""

import pytest
from pydantic import ValidationError

from InvPort.backend.models.schemas import (
    OptimizeRequest,
    SimulateRequest,
    AllocationItem,
    StockInfo,
)


class TestOptimizeRequest:
    def test_valid_request(self):
        req = OptimizeRequest(tickers=["AAPL", "MSFT"], risk_profile="bajo")
        assert req.tickers == ["AAPL", "MSFT"]
        assert req.risk_profile == "bajo"
        assert req.investment_amount == 10000.0
        assert req.method == "markowitz"

    def test_defaults(self):
        req = OptimizeRequest(tickers=["AAPL", "MSFT"], risk_profile="medio")
        assert req.investment_amount == 10000.0
        assert req.method == "markowitz"

    def test_all_methods(self):
        for method in ["markowitz", "genetic", "both"]:
            req = OptimizeRequest(tickers=["AAPL", "MSFT"], risk_profile="bajo", method=method)
            assert req.method == method

    def test_all_risk_profiles(self):
        for profile in ["bajo", "medio", "alto"]:
            req = OptimizeRequest(tickers=["AAPL", "MSFT"], risk_profile=profile)
            assert req.risk_profile == profile

    def test_min_tickers(self):
        with pytest.raises(ValidationError):
            OptimizeRequest(tickers=["AAPL"], risk_profile="bajo")

    def test_max_tickers(self):
        tickers = [f"T{i}" for i in range(16)]
        with pytest.raises(ValidationError):
            OptimizeRequest(tickers=tickers, risk_profile="bajo")

    def test_invalid_risk_profile(self):
        with pytest.raises(ValidationError):
            OptimizeRequest(tickers=["AAPL", "MSFT"], risk_profile="invalid")

    def test_invalid_method(self):
        with pytest.raises(ValidationError):
            OptimizeRequest(tickers=["AAPL", "MSFT"], risk_profile="bajo", method="invalid")


class TestSimulateRequest:
    def test_valid_request(self):
        req = SimulateRequest(tickers=["AAPL", "MSFT"], weights=[0.6, 0.4])
        assert req.days == 252
        assert req.n_simulations == 1000

    def test_custom_params(self):
        req = SimulateRequest(
            tickers=["AAPL"], weights=[1.0],
            investment_amount=50000, days=504, n_simulations=500,
        )
        assert req.investment_amount == 50000
        assert req.days == 504
        assert req.n_simulations == 500


class TestAllocationItem:
    def test_valid(self):
        item = AllocationItem(
            ticker="AAPL", company_name="Apple Inc.",
            weight=0.5, amount=5000.0, expected_return=0.15,
        )
        assert item.ticker == "AAPL"
        assert item.weight == 0.5


class TestStockInfo:
    def test_without_price(self):
        info = StockInfo(ticker="AAPL", name="Apple Inc.")
        assert info.current_price is None

    def test_with_price(self):
        info = StockInfo(ticker="AAPL", name="Apple Inc.", current_price=175.50)
        assert info.current_price == 175.50
