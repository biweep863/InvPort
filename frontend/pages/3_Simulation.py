"""Page 3: Monte Carlo simulation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from frontend.components.charts import monte_carlo_fan_chart
from backend.services.optimizer import run_simulation
from backend.models.schemas import SimulateRequest

st.set_page_config(page_title="Simulation - Optimizer", layout="wide")
st.title("Monte Carlo Simulation")

if "optimization_result" not in st.session_state:
    st.warning("First run an optimization on the Selection page.")
    st.stop()

data = st.session_state["optimization_result"]
result = data[0] if isinstance(data, list) else data
investment = st.session_state.get("investment_amount", 10000)

st.markdown("""
The **Monte Carlo Simulation** generates thousands of possible scenarios for your
optimized portfolio, allowing you to visualize the range of future outcomes.
""")

# --- Parameters ---
col1, col2 = st.columns(2)
with col1:
    years = st.slider("Time horizon (years)", min_value=1, max_value=5, value=1)
with col2:
    n_sims = st.slider("Number of simulations", min_value=500, max_value=5000, value=1000, step=500)

days = years * 252

if st.button("Run Simulation", type="primary", use_container_width=True):
    weights = [a["weight"] for a in result["allocations"]]
    tickers_ordered = [a["ticker"] for a in result["allocations"]]

    with st.spinner(f"Running {n_sims} simulations for {years} year(s)..."):
        try:
            req = SimulateRequest(
                tickers=tickers_ordered,
                weights=weights,
                investment_amount=investment,
                days=days,
                n_simulations=n_sims,
            )
            sim_data = run_simulation(req).model_dump()

            st.markdown("---")

            # Primary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Expected Final Value",
                    f"${sim_data['expected_final']:,.0f}",
                    delta=f"${sim_data['expected_final'] - investment:,.0f}",
                )
            with col2:
                st.metric(
                    "Probability of Loss",
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
                    "Expected Gain",
                    f"{gain_pct:.1f}%",
                )

            # Extended risk metrics
            st.markdown("---")
            st.subheader("Advanced Risk Analysis")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("CVaR 95%", f"${sim_data.get('cvar_95', 0):,.0f}")
                st.caption("Expected loss in the worst 5% of scenarios")
            with col2:
                st.metric("Median Drawdown", f"{sim_data.get('max_drawdown_median', 0) * 100:.1f}%")
                st.caption("Typical maximum drop during the period")
            with col3:
                st.metric("Extreme Drawdown (95%)", f"{sim_data.get('max_drawdown_95', 0) * 100:.1f}%")
                st.caption("Maximum drop in the worst 5% of scenarios")
            with col4:
                worst = sim_data.get("worst_case_final", 0)
                best = sim_data.get("best_case_final", 0)
                st.metric("Range 1%-99%", f"${worst:,.0f} - ${best:,.0f}")
                st.caption("Near-complete range of final outcomes")

            st.markdown("---")

            # Fan chart
            fig = monte_carlo_fan_chart(sim_data["percentiles"], days, investment)
            st.plotly_chart(fig, use_container_width=True)

            # Interpretation
            st.markdown("### Interpretation")
            st.markdown(f"""
            - **Light blue band**: 90% of scenarios fall within this range (5th-95th percentiles)
            - **Dark blue band**: 50% of scenarios fall here (25th-75th percentiles)
            - **Center line**: The median expected portfolio value
            - There is a **{sim_data['prob_loss']*100:.1f}%** probability of ending with less than invested
            - In the worst 5% of scenarios, you could lose up to **${sim_data['var_95']:,.0f}** (VaR)
            - The average loss in those worst scenarios would be **${sim_data.get('cvar_95', 0):,.0f}** (CVaR)
            """)

        except Exception as e:
            st.error(f"Error: {e}")
