# InvPort - S&P 500 Portfolio Optimizer

Investment portfolio optimization tool that uses Markowitz and genetic algorithms to find the optimal asset allocation from S&P 500 stocks, with Monte Carlo simulations, historical backtesting, and advanced risk analysis.

## Features

- **Markowitz Optimization** -- Mean-variance with target volatility constraints
- **Genetic Algorithm** -- Heuristic optimization with tournament selection and uniform crossover
- **Monte Carlo Simulation** -- Portfolio value projection with percentile bands and extended risk metrics (CVaR, drawdown)
- **Historical Backtest** -- Comparison of the optimized portfolio vs SPY using real data from the last 2 years
- **Efficient Frontier** -- Visualization of the optimal risk-return relationship
- **Individual Stock Analysis** -- Return, volatility, Sharpe, beta, drawdown, and 52-week range per stock
- **Advanced Metrics** -- Sortino, Calmar, Treynor, Information Ratio, Jensen's Alpha, Beta, CVaR, risk contribution
- **100+ S&P 500 stocks** organized by sector (Tech, Finance, Healthcare, Energy, etc.)
- **3 risk profiles**: Conservative (10% vol), Balanced (18% vol), Aggressive (30% vol)
- **Real-time data** from Yahoo Finance with 1-hour TTL cache

## Tech Stack

| Component      | Technology               |
| -------------- | ------------------------ |
| Backend API    | FastAPI + Uvicorn        |
| Frontend       | Streamlit                |
| Financial Data | yfinance (Yahoo Finance) |
| Optimization   | SciPy (SLSQP) + NumPy    |
| Visualization  | Plotly                   |
| Validation     | Pydantic                 |

## Requirements

- Python 3.11+

## Installation

```bash
git clone <repo-url>
cd InvPort

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

## Usage

You need **two terminals**:

```bash
# Terminal 1: Backend API (port 8000)
uvicorn InvPort.backend.main:app --reload --port 8000

# Terminal 2: Frontend Streamlit (port 8501)
streamlit run frontend/app.py
```

Open http://localhost:8501 in your browser.

## Project Structure

```
InvPort/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Constants, risk profiles, tickers
│   ├── models/
│   │   ├── portfolio.py     # Markowitz, genetic, Monte Carlo, efficient frontier
│   │   ├── metrics.py       # Sortino, drawdown, CVaR, beta, alpha, etc.
│   │   ├── backtest.py      # Historical backtesting vs benchmark
│   │   └── schemas.py       # Pydantic models (request/response)
│   ├── routers/
│   │   ├── stocks.py        # Stock endpoints and individual analysis
│   │   └── optimize.py      # Optimization, simulation, backtest endpoints
│   └── services/
│       ├── market_data.py   # Yahoo Finance wrapper with cache
│       └── optimizer.py     # Service orchestrator
├── frontend/
│   ├── app.py               # Streamlit main page
│   ├── components/
│   │   ├── charts.py        # Plotly charts (pie, frontier, heatmap, fan, backtest, drawdown, risk)
│   │   ├── stock_picker.py  # Stock selector by sector
│   │   └── risk_slider.py   # Risk profile selector
│   └── pages/
│       ├── 1_Selection.py   # Stock selection + individual analysis
│       ├── 2_Results.py     # Dashboard with basic and advanced metrics
│       ├── 3_Simulation.py  # Monte Carlo simulation with extended risk
│       └── 4_Backtest.py    # Historical backtest vs SPY
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── test_portfolio.py    # Optimization algorithm tests
│   ├── test_metrics.py      # Financial metrics tests
│   ├── test_schemas.py      # Pydantic validation tests
│   ├── test_market_data.py  # Data service tests
│   └── test_api.py          # Endpoint tests
├── requirements.txt
└── README.md
```

## API Endpoints

| Method | Route                          | Description                                             |
| ------ | ------------------------------ | ------------------------------------------------------- |
| `GET`  | `/`                            | Health check                                            |
| `GET`  | `/api/stocks/`                 | List stocks (optional filter `?q=`)                     |
| `GET`  | `/api/stocks/{ticker}/history` | Price history                                           |
| `POST` | `/api/stocks/analyze`          | Individual stock analysis (return, vol, beta, drawdown) |
| `POST` | `/api/optimize`                | Optimize portfolio with extended metrics                |
| `POST` | `/api/simulate`                | Monte Carlo simulation with CVaR and drawdown           |
| `POST` | `/api/backtest`                | Historical backtest vs SPY                              |

## Available Metrics

**Portfolio:**

- Expected annual return, Annual volatility, Sharpe Ratio
- Sortino Ratio (penalizes only downside volatility)
- Max Drawdown (largest drop from a peak)
- Calmar Ratio (return / max drawdown)
- CVaR 95% / Expected Shortfall (expected loss in the worst 5%)
- Beta (market sensitivity vs SPY)
- Jensen's Alpha (return above what CAPM predicts)
- Treynor Ratio (return per unit of systematic risk)
- Information Ratio (active return / tracking error)
- Risk contribution per stock

**Simulation:**

- VaR 95%, CVaR 95%, probability of loss
- Median and extreme drawdown (95th percentile) across simulations
- Final outcome range (1st-99th percentile)

## Tests

```bash
pip install pytest httpx

# Run all tests
pytest

# Verbose
pytest -v

# With coverage
pip install pytest-cov
pytest --cov=backend
```

## Application Flow

1. **Selection** -- Choose 2-15 stocks, analyze their individual statistics, select risk profile
2. **Optimization** -- The backend downloads data from Yahoo Finance, computes returns/covariance, runs the algorithm, and calculates all metrics
3. **Results** -- Basic and advanced metrics, allocation, risk contribution, efficient frontier, correlation
4. **Simulation** -- Monte Carlo with extended risk metrics (CVaR, drawdown, scenario range)
5. **Backtest** -- Historical portfolio performance vs SPY with drawdown chart
