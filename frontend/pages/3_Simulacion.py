"""Page 3: Monte Carlo simulation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import requests

from InvPort.frontend.components.charts import monte_carlo_fan_chart

st.set_page_config(page_title="Simulación - Optimizador", page_icon="🎲", layout="wide")
st.title("🎲 Simulación Monte Carlo")

# Check for results
if "optimization_result" not in st.session_state:
    st.warning("⚠️ Primero ejecuta una optimización en la página **Selección**.")
    st.stop()

data = st.session_state["optimization_result"]
result = data[0] if isinstance(data, list) else data
investment = st.session_state.get("investment_amount", 10000)
tickers = st.session_state.get("selected_tickers", [])

st.markdown("""
La **Simulación Monte Carlo** genera miles de escenarios posibles para tu portafolio
optimizado, permitiéndote visualizar el rango de resultados futuros.
""")

# --- Parameters ---
col1, col2 = st.columns(2)
with col1:
    years = st.slider("Horizonte temporal (años)", min_value=1, max_value=5, value=1)
with col2:
    n_sims = st.slider("Número de simulaciones", min_value=500, max_value=5000, value=1000, step=500)

days = years * 252

API_URL = "http://localhost:8000"

if st.button("🎲 Ejecutar Simulación", type="primary", use_container_width=True):
    weights = [a["weight"] for a in result["allocations"]]
    tickers_ordered = [a["ticker"] for a in result["allocations"]]

    with st.spinner(f"Ejecutando {n_sims} simulaciones para {years} año(s)..."):
        try:
            response = requests.post(
                f"{API_URL}/api/simulate",
                json={
                    "tickers": tickers_ordered,
                    "weights": weights,
                    "investment_amount": investment,
                    "days": days,
                    "n_simulations": n_sims,
                },
                timeout=180,
            )
            response.raise_for_status()
            sim_data = response.json()

            # --- Results ---
            st.markdown("---")

            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Valor Esperado Final",
                    f"${sim_data['expected_final']:,.0f}",
                    delta=f"${sim_data['expected_final'] - investment:,.0f}",
                )
            with col2:
                st.metric(
                    "Probabilidad de Pérdida",
                    f"{sim_data['prob_loss'] * 100:.1f}%",
                )
            with col3:
                st.metric(
                    "VaR 95% (Valor en Riesgo)",
                    f"${sim_data['var_95']:,.0f}",
                )
            with col4:
                gain_pct = ((sim_data["expected_final"] / investment) - 1) * 100
                st.metric(
                    "Ganancia Esperada",
                    f"{gain_pct:.1f}%",
                )

            st.markdown("---")

            # Fan chart
            fig = monte_carlo_fan_chart(sim_data["percentiles"], days, investment)
            st.plotly_chart(fig, use_container_width=True)

            # Interpretation
            st.markdown("### 📖 Interpretación")
            st.markdown(f"""
            - **Banda azul clara**: El 90% de los escenarios caen en este rango (percentiles 5-95)
            - **Banda azul oscura**: El 50% de los escenarios caen aquí (percentiles 25-75)
            - **Línea central**: La mediana esperada del portafolio
            - Hay un **{sim_data['prob_loss']*100:.1f}%** de probabilidad de terminar con menos de lo invertido
            - En el peor 5% de escenarios, podrías perder hasta **${sim_data['var_95']:,.0f}**
            """)

        except requests.exceptions.ConnectionError:
            st.error(
                "❌ No se pudo conectar al servidor API. "
                "Asegúrate de que el backend esté corriendo:\n\n"
                "`uvicorn backend.main:app --reload --port 8000`"
            )
        except Exception as e:
            st.error(f"❌ Error: {e}")
