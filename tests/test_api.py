"""Tests for API endpoints."""

import pytest


class TestRootEndpoint:
    def test_health_check(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestStocksEndpoints:
    def test_list_all_stocks(self, client):
        response = client.get("/api/stocks/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "ticker" in data[0]
        assert "name" in data[0]

    def test_search_stocks(self, client):
        response = client.get("/api/stocks/?q=apple")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any("Apple" in s["name"] for s in data)

    def test_search_no_results(self, client):
        response = client.get("/api/stocks/?q=xyznonexistent")
        assert response.status_code == 200
        assert response.json() == []

    def test_search_by_ticker(self, client):
        response = client.get("/api/stocks/?q=AAPL")
        assert response.status_code == 200
        data = response.json()
        assert any(s["ticker"] == "AAPL" for s in data)


class TestOptimizeEndpoint:
    def test_invalid_request_empty_tickers(self, client):
        response = client.post("/api/optimize", json={
            "tickers": [],
            "risk_profile": "bajo",
        })
        assert response.status_code == 422

    def test_invalid_risk_profile(self, client):
        response = client.post("/api/optimize", json={
            "tickers": ["AAPL", "MSFT"],
            "risk_profile": "invalid",
        })
        assert response.status_code == 422

    def test_single_ticker_rejected(self, client):
        response = client.post("/api/optimize", json={
            "tickers": ["AAPL"],
            "risk_profile": "bajo",
        })
        assert response.status_code == 422


class TestSimulateEndpoint:
    def test_invalid_request_missing_fields(self, client):
        response = client.post("/api/simulate", json={})
        assert response.status_code == 422
