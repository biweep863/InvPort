"""Stock data endpoints."""

from fastapi import APIRouter, Query

from InvPort.backend.config import SP500_TICKERS
from InvPort.backend.models.schemas import StockInfo
from InvPort.backend.services.market_data import fetch_historical

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/", response_model=list[StockInfo])
async def list_stocks(q: str = Query(default="", description="Search filter")):
    """List available S&P 500 stocks, optionally filtered by search query."""
    results = []
    q_lower = q.lower()
    for ticker, name in SP500_TICKERS.items():
        if q and q_lower not in ticker.lower() and q_lower not in name.lower():
            continue
        results.append(StockInfo(ticker=ticker, name=name))
    return results


@router.get("/{ticker}/history")
async def stock_history(ticker: str, period: str = "2y"):
    """Get historical price data for a single stock."""
    prices = fetch_historical([ticker], period=period)
    records = []
    for date, row in prices.iterrows():
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "close": round(float(row.iloc[0]), 2),
        })
    return {"ticker": ticker, "history": records}
