"""Page 3: Monte Carlo simulation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import streamlit as st
import requests

from InvPort.frontend.components.charts import monte_carlo_fan_chart

st.set_page_config(page_title="Simulacion - Optimizador", layout="wide")
st.title("Simulacion Monte Carlo")

if "optimization_result" not in st.session_state:
    st.warning("Primero ejecuta una optimizacion en la pagina Seleccion.")
    st.stop()

data = st.session_state["optimization_result"]
result = data[0] if isinstance(data, list) else data
investment = st.session_state.get("investment_amount", 10000)

st.markdown("""
La **Simulacion Monte Carlo** genera miles de escenarios posibles para tu portafolio
optimizado, permitiendote visualizar el rango de resultados futuros.
""")

# --- Parameters ---
col1, col2 = st.columns(2)
with col1:
    years = st.slider("Horizonte temporal (anos)", min_value=1, max_value=5, value=1)
with col2:
    n_sims = st.slider("Numero de simulaciones", min_value=500, max_value=5000, value=1000, step=500)

days = years * 252

API_URL = "http://localhost:8000"

if st.button("Ejecutar Simulacion", type="primary", use_container_width=True):
    weights = [a["weight"] for a in result["allocations"]]
    tickers_ordered = [a["ticker"] for a in result["allocations"]]

    with st.spinner(f"Ejecutando {n_sims} simulaciones para {years} ano(s)..."):
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

            st.markdown("---")

            # Primary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Valor Esperado Final",
                    f"${sim_data['expected_final']:,.0f}",
                    delta=f"${sim_data['expected_final'] - investment:,.0f}",
                )
            with col2:
                st.metric(
                    "Probabilidad de Perdida",
                    f"{sim_data['prob_loss'] * 100:.1f}%",
                )
            with col3:
                st.metric(
                    "VaR 95%",
                    f"${sim_data['var_95']:,.0f}",
                )
            with col4:
                gain_pct = ((sim_data["expected_final"] / investment) - 1) * 100
                st.metric(
                    "Ganancia Esperada",
                    f"{gain_pct:.1f}%",
                )

            # Extended risk metrics
            st.markdown("---")
            st.subheader("Analisis de Riesgo Avanzado")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("CVaR 95%", f"${sim_data.get('cvar_95', 0):,.0f}")
                st.caption("Perdida esperada en el peor 5% de escenarios")
            with col2:
                st.metric("Drawdown Mediano", f"{sim_data.get('max_drawdown_median', 0) * 100:.1f}%")
                st.caption("Caida tipica maxima durante el periodo")
            with col3:
                st.metric("Drawdown Extremo (95%)", f"{sim_data.get('max_drawdown_95', 0) * 100:.1f}%")
                st.caption("Caida maxima en el peor 5% de escenarios")
            with col4:
                worst = sim_data.get("worst_case_final", 0)
                best = sim_data.get("best_case_final", 0)
                st.metric("Rango 1%-99%", f"${worst:,.0f} - ${best:,.0f}")
                st.caption("Rango casi completo de resultados finales")

            st.markdown("---")

            # Fan chart
            fig = monte_carlo_fan_chart(sim_data["percentiles"], days, investment)
            st.plotly_chart(fig, use_container_width=True)

            # Interpretation
            st.markdown("### Interpretacion")
            st.markdown(f"""
            - **Banda azul clara**: El 90% de los escenarios caen en este rango (percentiles 5-95)
            - **Banda azul oscura**: El 50% de los escenarios caen aqui (percentiles 25-75)
            - **Linea central**: La mediana esperada del portafolio
            - Hay un **{sim_data['prob_loss']*100:.1f}%** de probabilidad de terminar con menos de lo invertido
            - En el peor 5% de escenarios, podrias perder hasta **${sim_data['var_95']:,.0f}** (VaR)
            - La perdida promedio en esos peores escenarios seria **${sim_data.get('cvar_95', 0):,.0f}** (CVaR)
            """)

        except requests.exceptions.ConnectionError:
            st.error(
                "No se pudo conectar al servidor API. "
                "Asegurate de que el backend este corriendo:\n\n"
                "`uvicorn backend.main:app --reload --port 8000`"
            )
        except Exception as e:
            st.error(f"Error: {e}")
