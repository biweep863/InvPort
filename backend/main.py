"""FastAPI application entry point."""

from backend.routers import optimize
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import stocks

app = FastAPI(
    title="S&P 500 Portfolio Optimizer",
    description="API for smart investment portfolio optimization",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router)
app.include_router(optimize.router)


@app.get("/")
async def root():
    return {"status": "ok", "app": "Portfolio Optimizer API", "version": "1.0.0"}
