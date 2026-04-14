"""FastAPI application entry point."""

from InvPort.backend.routers import optimize
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from InvPort.backend.routers import stocks

app = FastAPI(
    title="Optimizador de Portafolios S&P 500",
    description="API para optimización inteligente de portafolios de inversión",
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
