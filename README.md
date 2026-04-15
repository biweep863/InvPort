# InvPort - Optimizador de Portafolios S&P 500

Herramienta de optimizacion de portafolios de inversion que utiliza algoritmos de Markowitz y geneticos para encontrar la distribucion optima de activos del S&P 500, con simulaciones Monte Carlo, backtesting historico y analisis de riesgo avanzado.

## Caracteristicas

- **Optimizacion Markowitz** -- Media-varianza con restricciones de volatilidad objetivo
- **Algoritmo Genetico** -- Optimizacion heuristica con seleccion por torneo y crossover uniforme
- **Simulacion Monte Carlo** -- Proyeccion de valor del portafolio con bandas de percentiles y metricas de riesgo extendidas (CVaR, drawdown)
- **Backtest Historico** -- Comparacion del portafolio optimizado vs SPY usando datos reales de los ultimos 2 anos
- **Frontera Eficiente** -- Visualizacion de la relacion riesgo-retorno optima
- **Analisis Individual de Acciones** -- Retorno, volatilidad, Sharpe, beta, drawdown y rango 52 semanas por accion
- **Metricas Avanzadas** -- Sortino, Calmar, Treynor, Information Ratio, Alpha de Jensen, Beta, CVaR, contribucion al riesgo
- **100+ acciones del S&P 500** organizadas por sector (Tech, Finanzas, Salud, Energia, etc.)
- **3 perfiles de riesgo**: Conservador (10% vol), Balanceado (18% vol), Agresivo (30% vol)
- **Datos en tiempo real** de Yahoo Finance con cache TTL de 1 hora

## Tech Stack

| Componente | Tecnologia |
|------------|------------|
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Datos financieros | yfinance (Yahoo Finance) |
| Optimizacion | SciPy (SLSQP) + NumPy |
| Visualizacion | Plotly |
| Validacion | Pydantic |

## Requisitos

- Python 3.11+

## Instalacion

```bash
git clone <url-del-repo>
cd InvPort

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

## Uso

Se necesitan **dos terminales**:

```bash
# Terminal 1: Backend API (puerto 8000)
uvicorn InvPort.backend.main:app --reload --port 8000

# Terminal 2: Frontend Streamlit (puerto 8501)
streamlit run frontend/app.py
```

Abre http://localhost:8501 en tu navegador.

## Estructura del Proyecto

```
InvPort/
├── backend/
│   ├── main.py              # Entry point FastAPI
│   ├── config.py            # Constantes, perfiles de riesgo, tickers
│   ├── models/
│   │   ├── portfolio.py     # Markowitz, genetico, Monte Carlo, frontera eficiente
│   │   ├── metrics.py       # Sortino, drawdown, CVaR, beta, alpha, etc.
│   │   ├── backtest.py      # Backtesting historico vs benchmark
│   │   └── schemas.py       # Modelos Pydantic (request/response)
│   ├── routers/
│   │   ├── stocks.py        # Endpoints de acciones y analisis individual
│   │   └── optimize.py      # Endpoints de optimizacion, simulacion, backtest
│   └── services/
│       ├── market_data.py   # Yahoo Finance wrapper con cache
│       └── optimizer.py     # Orquestador de servicios
├── frontend/
│   ├── app.py               # Pagina principal Streamlit
│   ├── components/
│   │   ├── charts.py        # Graficos Plotly (pie, frontera, heatmap, fan, backtest, drawdown, riesgo)
│   │   ├── stock_picker.py  # Selector de acciones por sector
│   │   └── risk_slider.py   # Selector de perfil de riesgo
│   └── pages/
│       ├── 1_Seleccion.py   # Seleccion + analisis individual de acciones
│       ├── 2_Resultados.py  # Dashboard con metricas basicas y avanzadas
│       ├── 3_Simulacion.py  # Simulacion Monte Carlo con riesgo extendido
│       └── 4_Backtest.py    # Backtest historico vs SPY
├── tests/
│   ├── conftest.py          # Fixtures compartidos
│   ├── test_portfolio.py    # Tests de algoritmos de optimizacion
│   ├── test_metrics.py      # Tests de metricas financieras
│   ├── test_schemas.py      # Tests de validacion Pydantic
│   ├── test_market_data.py  # Tests del servicio de datos
│   └── test_api.py          # Tests de endpoints
├── requirements.txt
└── README.md
```

## API Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/api/stocks/` | Listar acciones (filtro opcional `?q=`) |
| `GET` | `/api/stocks/{ticker}/history` | Historial de precios |
| `POST` | `/api/stocks/analyze` | Analisis individual de acciones (retorno, vol, beta, drawdown) |
| `POST` | `/api/optimize` | Optimizar portafolio con metricas extendidas |
| `POST` | `/api/simulate` | Simulacion Monte Carlo con CVaR y drawdown |
| `POST` | `/api/backtest` | Backtest historico vs SPY |

## Metricas Disponibles

**Portafolio:**
- Retorno esperado anual, Volatilidad anual, Ratio de Sharpe
- Ratio de Sortino (penaliza solo volatilidad negativa)
- Max Drawdown (mayor caida desde un maximo)
- Ratio Calmar (retorno / max drawdown)
- CVaR 95% / Expected Shortfall (perdida esperada en el peor 5%)
- Beta (sensibilidad al mercado vs SPY)
- Alpha de Jensen (retorno por encima de lo que CAPM predice)
- Ratio Treynor (retorno por unidad de riesgo sistematico)
- Information Ratio (retorno activo / tracking error)
- Contribucion al riesgo por accion

**Simulacion:**
- VaR 95%, CVaR 95%, probabilidad de perdida
- Drawdown mediano y extremo (percentil 95) across simulaciones
- Rango de resultados finales (percentil 1-99)

## Tests

```bash
pip install pytest httpx

# Correr todos los tests
pytest

# Con verbose
pytest -v

# Con cobertura
pip install pytest-cov
pytest --cov=backend
```

## Flujo de la Aplicacion

1. **Seleccion** -- Elige 2-15 acciones, analiza sus estadisticas individuales, selecciona perfil de riesgo
2. **Optimizacion** -- El backend descarga datos de Yahoo Finance, calcula retornos/covarianza, ejecuta el algoritmo y computa todas las metricas
3. **Resultados** -- Metricas basicas y avanzadas, asignacion, contribucion al riesgo, frontera eficiente, correlacion
4. **Simulacion** -- Monte Carlo con metricas de riesgo extendidas (CVaR, drawdown, rango de escenarios)
5. **Backtest** -- Rendimiento historico del portafolio vs SPY con grafico de drawdown
