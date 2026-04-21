<div align="center">

# InvPort

### S&P 500 Portfolio Optimizer

An investment portfolio optimization tool powered by **Markowitz mean-variance analysis** and **genetic algorithms**.  
Find optimal asset allocations from 100+ S&P 500 stocks with Monte Carlo simulations, historical backtesting, and advanced risk analytics.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)

</div>

---

## Features

| Category | Details |
|----------|---------|
| **Markowitz Optimization** | Mean-variance with target volatility constraints |
| **Genetic Algorithm** | Heuristic optimization with tournament selection and uniform crossover |
| **Monte Carlo Simulation** | Portfolio projection with percentile bands, CVaR, and drawdown |
| **Historical Backtest** | Optimized portfolio vs SPY using 2 years of real data |
| **Efficient Frontier** | Visualization of the optimal risk-return tradeoff |
| **Stock Analysis** | Return, volatility, Sharpe, beta, drawdown, and 52-week range per stock |
| **Advanced Metrics** | Sortino, Calmar, Treynor, Information Ratio, Jensen's Alpha, CVaR, and more |

> **100+ S&P 500 stocks** organized by sector &bull; **3 risk profiles** (Conservative / Balanced / Aggressive) &bull; **Real-time data** from Yahoo Finance with 1-hour cache

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Financial Data | yfinance (Yahoo Finance) |
| Optimization | SciPy (SLSQP) + NumPy |
| Visualization | Plotly |
| Validation | Pydantic |

---

## Getting Started

### Prerequisites

- Python 3.11+

### Installation

```bash
git clone <repo-url>
cd InvPort

python -m venv .venv
source .venv/bin/activate    # Linux / macOS
# .venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### Running Locally

**Option A -- Streamlit only** (simplest, same as cloud deployment):

```bash
streamlit run frontend/app.py
```

**Option B -- Streamlit + FastAPI** (if you want to use the REST API separately):

```bash
# Terminal 1
uvicorn backend.main:app --reload --port 8000

# Terminal 2
streamlit run frontend/app.py
```

Then open **http://localhost:8501** in your browser.

### Deploying to Streamlit Cloud

1. Push your repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Set the **Main file path** to `frontend/app.py`
4. Deploy -- no separate backend needed, everything runs in one process

---

## How It Works

```
1. Select       2. Optimize       3. Analyze       4. Simulate       5. Backtest
   Stocks          Portfolio         Results          Monte Carlo        vs SPY
```

1. **Selection** -- Pick 2-15 stocks, review individual statistics, choose a risk profile
2. **Optimization** -- Fetches data from Yahoo Finance, computes returns and covariance, runs the optimizer, and calculates all metrics
3. **Results** -- Allocation breakdown, risk contribution, efficient frontier, correlation heatmap, and full metrics dashboard
4. **Simulation** -- Monte Carlo projection with extended risk metrics (CVaR, drawdown, scenario range)
5. **Backtest** -- Historical portfolio performance vs SPY with drawdown chart

---

## Available Metrics

<details>
<summary><strong>Portfolio Metrics</strong></summary>

| Metric | Description |
|--------|-------------|
| Expected Annual Return | Annualized mean return |
| Annual Volatility | Standard deviation of returns |
| Sharpe Ratio | Risk-adjusted return (excess return / volatility) |
| Sortino Ratio | Penalizes only downside volatility |
| Max Drawdown | Largest peak-to-trough decline |
| Calmar Ratio | Return / max drawdown |
| CVaR 95% | Expected loss in the worst 5% of scenarios |
| Beta | Market sensitivity vs SPY |
| Jensen's Alpha | Return above CAPM prediction |
| Treynor Ratio | Return per unit of systematic risk |
| Information Ratio | Active return / tracking error |
| Risk Contribution | Per-stock contribution to total portfolio risk |

</details>

<details>
<summary><strong>Simulation Metrics</strong></summary>

| Metric | Description |
|--------|-------------|
| VaR 95% | Value at Risk at the 95th percentile |
| CVaR 95% | Conditional Value at Risk |
| Probability of Loss | Likelihood of negative returns |
| Median Drawdown | Median max drawdown across simulations |
| Extreme Drawdown | 95th percentile drawdown |
| Final Outcome Range | 1st to 99th percentile of final portfolio values |

</details>

---

## API Reference

The FastAPI backend exposes these endpoints (available when running with Option B):

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/api/stocks/` | List stocks (optional filter `?q=`) |
| `GET` | `/api/stocks/{ticker}/history` | Price history |
| `POST` | `/api/stocks/analyze` | Individual stock analysis |
| `POST` | `/api/optimize` | Portfolio optimization with extended metrics |
| `POST` | `/api/simulate` | Monte Carlo simulation with CVaR and drawdown |
| `POST` | `/api/backtest` | Historical backtest vs SPY |

---

## Project Structure

```
InvPort/
├── backend/
│   ├── main.py                # FastAPI entry point
│   ├── config.py              # Constants, risk profiles, tickers
│   ├── models/
│   │   ├── portfolio.py       # Markowitz, genetic, Monte Carlo, efficient frontier
│   │   ├── metrics.py         # Sortino, drawdown, CVaR, beta, alpha, etc.
│   │   ├── backtest.py        # Historical backtesting vs benchmark
│   │   └── schemas.py         # Pydantic request/response models
│   ├── routers/
│   │   ├── stocks.py          # Stock endpoints and individual analysis
│   │   └── optimize.py        # Optimization, simulation, backtest endpoints
│   └── services/
│       ├── market_data.py     # Yahoo Finance wrapper with cache
│       └── optimizer.py       # Service orchestrator
├── frontend/
│   ├── app.py                 # Streamlit main page
│   ├── components/
│   │   ├── charts.py          # Plotly charts (pie, frontier, heatmap, etc.)
│   │   ├── stock_picker.py    # Stock selector by sector
│   │   └── risk_slider.py     # Risk profile selector
│   └── pages/
│       ├── 1_Selection.py     # Stock selection + individual analysis
│       ├── 2_Results.py       # Metrics dashboard and allocation
│       ├── 3_Simulation.py    # Monte Carlo simulation
│       └── 4_Backtest.py      # Historical backtest vs SPY
├── tests/
│   ├── conftest.py            # Shared fixtures
│   ├── test_portfolio.py      # Optimization algorithm tests
│   ├── test_metrics.py        # Financial metrics tests
│   ├── test_schemas.py        # Pydantic validation tests
│   ├── test_market_data.py    # Data service tests
│   └── test_api.py            # Endpoint tests
├── requirements.txt
└── README.md
```

---

## Testing

```bash
pip install pytest httpx

pytest           # Run all tests
pytest -v        # Verbose output
```

```bash
# With coverage
pip install pytest-cov
pytest --cov=backend
```

---

<div align="center">
<sub>Built with FastAPI, Streamlit, and Plotly</sub>
</div>
