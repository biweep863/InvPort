"""Page 4: Historical backtesting."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import streamlit as st
import requests

from InvPort.frontend.components.charts import backtest_chart, drawdown_chart

st.set_page_config(page_title="Backtest - Optimizer", layout="wide")
st.title("Historical Backtest")

if "optimization_result" not in st.session_state:
    st.warning("First run an optimization on the Selection page.")
    st.stop()

data = st.session_state["optimization_result"]
result = data[0] if isinstance(data, list) else data
investment = st.session_state.get("investment_amount", 10000)

st.markdown("""
The **Historical Backtest** shows how your optimized portfolio would have performed
over the last 2 years, compared against the S&P 500 index (SPY).

**Note:** Past results do not guarantee future returns.
""")

API_URL = "http://localhost:8000"

if st.button("Run Backtest", type="primary", use_container_width=True):
    weights = [a["weight"] for a in result["allocations"]]
    tickers_ordered = [a["ticker"] for a in result["allocations"]]

    with st.spinner("Running historical backtest..."):
        try:
            response = requests.post(
                f"{API_URL}/api/backtest",
                json={
                    "tickers": tickers_ordered,
                    "weights": weights,
                    "investment_amount": investment,
                },
                timeout=120,
            )
            response.raise_for_status()
            bt = response.json()

            st.markdown("---")

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Total Return",
                    f"{bt['total_return'] * 100:.2f}%",
                    delta=f"vs SPY: {bt['benchmark_total_return'] * 100:.2f}%",
                )
            with col2:
                st.metric("Annualized Return", f"{bt['annualized_return'] * 100:.2f}%")
            with col3:
                st.metric("Max Drawdown", f"{bt['max_drawdown'] * 100:.2f}%")
                st.caption(f"Date: {bt['max_drawdown_date']}")
            with col4:
                st.metric("Best / Worst Day",
                    f"+{bt['best_day'] * 100:.2f}% / {bt['worst_day'] * 100:.2f}%")

            st.markdown("---")

            # Performance chart
            fig_perf = backtest_chart(bt["dates"], bt["portfolio_values"], bt["benchmark_values"])
            st.plotly_chart(fig_perf, use_container_width=True)

            # Drawdown chart
            fig_dd = drawdown_chart(bt["dates"], bt["drawdown_series"])
            st.plotly_chart(fig_dd, use_container_width=True)

            # Final values
            st.markdown("---")
            final_port = bt["portfolio_values"][-1]
            final_bench = bt["benchmark_values"][-1]
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Portfolio Final Value", f"${final_port:,.2f}")
            with col2:
                st.metric("SPY Final Value", f"${final_bench:,.2f}")

            outperformance = bt["total_return"] - bt["benchmark_total_return"]
            if outperformance > 0:
                st.success(f"Your portfolio outperformed SPY by {outperformance * 100:.2f} percentage points.")
            else:
                st.info(f"SPY outperformed your portfolio by {abs(outperformance) * 100:.2f} percentage points.")

        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to the API server. "
                "Make sure the backend is running:\n\n"
                "`uvicorn backend.main:app --reload --port 8000`"
            )
        except Exception as e:
            st.error(f"Error: {e}")
