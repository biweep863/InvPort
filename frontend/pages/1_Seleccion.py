"""Page 1: Stock selection and optimization parameters."""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import streamlit as st
import requests

from InvPort.backend.config import SP500_TICKERS, RISK_PROFILES
from InvPort.frontend.components.stock_picker import render_stock_picker
from InvPort.frontend.components.risk_slider import render_risk_slider

st.set_page_config(page_title="Seleccion - Optimizador", layout="wide")
st.title("Seleccion de Portafolio")

# --- Stock Picker ---
selected_tickers = render_stock_picker(SP500_TICKERS)

# --- Stock Analysis ---
API_URL = "http://localhost:8000"

if len(selected_tickers) >= 2:
    if st.button("Analizar Acciones Seleccionadas"):
        with st.spinner("Analizando acciones..."):
            try:
                resp = requests.post(
                    f"{API_URL}/api/stocks/analyze",
                    json=selected_tickers,
                    timeout=60,
                )
                resp.raise_for_status()
                analysis = resp.json()

                import pandas as pd
                df = pd.DataFrame([
                    {
                        "Ticker": a["ticker"],
                        "Precio": f"${a['current_price']:,.2f}",
                        "Retorno Anual": f"{a['annualized_return'] * 100:.1f}%",
                        "Volatilidad": f"{a['annualized_volatility'] * 100:.1f}%",
                        "Sharpe": f"{a['sharpe_ratio']:.2f}",
                        "Max Drawdown": f"{a['max_drawdown'] * 100:.1f}%",
                        "Beta": f"{a['beta']:.2f}",
                        "52W High": f"${a['high_52w']:,.2f}",
                        "52W Low": f"${a['low_52w']:,.2f}",
                    }
                    for a in analysis
                ])
                st.dataframe(df, use_container_width=True, hide_index=True)
            except requests.exceptions.ConnectionError:
                st.error("No se pudo conectar al API. Asegurate de que el backend este corriendo.")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# --- Risk Profile ---
risk_profile = render_risk_slider()

st.markdown("---")

# --- Investment Amount ---
st.subheader("Monto de Inversion")
investment = st.number_input(
    "Cuanto deseas invertir (USD)?",
    min_value=100.0,
    max_value=10_000_000.0,
    value=10_000.0,
    step=1000.0,
    format="%.2f",
)

# --- Method ---
st.subheader("Metodo de Optimizacion")
method = st.radio(
    "Selecciona el metodo:",
    options=["markowitz", "genetic", "both"],
    format_func=lambda x: {
        "markowitz": "Markowitz (Mean-Variance)",
        "genetic": "Algoritmo Genetico",
        "both": "Comparar Ambos",
    }[x],
    horizontal=True,
)

st.markdown("---")

# --- Optimize Button ---
if st.button("Optimizar Portafolio", type="primary", use_container_width=True):
    if len(selected_tickers) < 2:
        st.error("Selecciona al menos 2 acciones para continuar.")
    else:
        with st.spinner("Descargando datos y optimizando... Esto puede tomar unos segundos."):
            try:
                response = requests.post(
                    f"{API_URL}/api/optimize",
                    json={
                        "tickers": selected_tickers,
                        "risk_profile": risk_profile,
                        "investment_amount": investment,
                        "method": method,
                    },
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()

                # Store results in session state
                st.session_state["optimization_result"] = data
                st.session_state["selected_tickers"] = selected_tickers
                st.session_state["investment_amount"] = investment
                st.session_state["risk_profile"] = risk_profile
                st.session_state["method"] = method

                st.success("Optimizacion completada. Ve a la pagina Resultados para ver el analisis.")
                st.balloons()

            except requests.exceptions.ConnectionError:
                st.error(
                    "No se pudo conectar al servidor API. "
                    "Asegurate de que el backend este corriendo:\n\n"
                    "`uvicorn backend.main:app --reload --port 8000`"
                )
            except requests.exceptions.HTTPError as e:
                st.error(f"Error del servidor: {e}")
            except Exception as e:
                st.error(f"Error inesperado: {e}")
