# InvPort - Optimizador de Portafolios S&P 500

Herramienta de optimización de portafolios de inversión que utiliza algoritmos de Markowitz y genéticos para encontrar la distribución óptima de activos del S&P 500, con simulaciones Monte Carlo para análisis de riesgo.

## Características

- **Optimización Markowitz** — Media-varianza con restricciones de volatilidad objetivo
- **Algoritmo Genético** — Optimización heurística con selección por torneo y crossover uniforme
- **Simulación Monte Carlo** — Proyección de valor del portafolio con bandas de percentiles (5/25/50/75/95)
- **Frontera Eficiente** — Visualización de la relación riesgo-retorno óptima
- **50+ acciones del S&P 500** curadas y listas para seleccionar
- **3 perfiles de riesgo**: Conservador (10% vol), Balanceado (18% vol), Agresivo (30% vol)
- **Caché de datos** con TTL de 1 hora para minimizar llamadas a Yahoo Finance

## Tech Stack

| Componente | Tecnología |
|------------|------------|
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Datos financieros | yfinance (Yahoo Finance) |
| Optimización | SciPy (SLSQP) + NumPy |
| Visualización | Plotly |
| Validación | Pydantic |

## Requisitos

- Python 3.11+

## Instalación

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd InvPort

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

Se necesitan **dos terminales** para correr la aplicación:

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
│   ├── config.py            # Constantes y configuración
│   ├── models/
│   │   ├── portfolio.py     # Algoritmos de optimización
│   │   └── schemas.py       # Modelos Pydantic
│   ├── routers/
│   │   ├── stocks.py        # Endpoints de acciones
│   │   └── optimize.py      # Endpoints de optimización
│   └── services/
│       ├── market_data.py   # Wrapper de Yahoo Finance
│       └── optimizer.py     # Orquestador de servicios
├── frontend/
│   ├── app.py               # Página principal Streamlit
│   ├── components/
│   │   ├── charts.py        # Gráficos Plotly
│   │   ├── stock_picker.py  # Selector de acciones
│   │   └── risk_slider.py   # Selector de perfil de riesgo
│   └── pages/
│       ├── 1_Seleccion.py   # Selección de portafolio
│       ├── 2_Resultados.py  # Dashboard de resultados
│       └── 3_Simulacion.py  # Simulación Monte Carlo
├── tests/
│   ├── conftest.py          # Fixtures compartidos
│   ├── test_portfolio.py    # Tests de algoritmos
│   ├── test_schemas.py      # Tests de validación
│   ├── test_market_data.py  # Tests del servicio de datos
│   └── test_api.py          # Tests de endpoints
├── requirements.txt
└── README.md
```

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/api/stocks/` | Listar acciones (filtro opcional `?q=`) |
| `GET` | `/api/stocks/{ticker}/history` | Historial de precios |
| `POST` | `/api/optimize` | Ejecutar optimización |
| `POST` | `/api/simulate` | Ejecutar simulación Monte Carlo |

## Tests

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx

# Correr todos los tests
pytest

# Con cobertura
pip install pytest-cov
pytest --cov=backend

# Solo tests unitarios (sin llamadas a red)
pytest -m "not integration"
```

## Flujo de la Aplicación

1. **Selección** — El usuario elige 2-15 acciones y su perfil de riesgo
2. **Optimización** — El backend descarga datos históricos, calcula retornos y covarianza, y ejecuta el algoritmo seleccionado
3. **Resultados** — Se muestra la asignación óptima, métricas de rendimiento, frontera eficiente y mapa de correlación
4. **Simulación** — Monte Carlo proyecta el valor futuro del portafolio con bandas de confianza
