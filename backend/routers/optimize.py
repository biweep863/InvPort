"""Portfolio optimization endpoints."""

from fastapi import APIRouter

from InvPort.backend.models.schemas import (
    BacktestRequest,
    BacktestResponse,
    OptimizeRequest,
    OptimizeResponse,
    SimulateRequest,
    SimulateResponse,
)
from InvPort.backend.services.optimizer import run_optimization, run_simulation, run_backtest_service

router = APIRouter(prefix="/api", tags=["optimize"])


@router.post("/optimize", response_model=OptimizeResponse | list[OptimizeResponse])
async def optimize(req: OptimizeRequest):
    """Optimize a portfolio based on selected stocks and risk profile."""
    return run_optimization(req)


@router.post("/simulate", response_model=SimulateResponse)
async def simulate(req: SimulateRequest):
    """Run Monte Carlo simulation on a portfolio."""
    return run_simulation(req)


@router.post("/backtest", response_model=BacktestResponse)
async def backtest(req: BacktestRequest):
    """Run historical backtest on a portfolio."""
    return run_backtest_service(req)
