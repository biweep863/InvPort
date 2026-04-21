"""Page 1: Stock selection and optimization parameters."""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import pandas as pd

from backend.config import SP500_TICKERS, RISK_PROFILES
from backend.services.optimizer import analyze_stocks, run_optimization
from backend.models.schemas import OptimizeRequest
from frontend.components.stock_picker import render_stock_picker
from frontend.components.risk_slider import render_risk_slider

st.set_page_config(page_title="Selection - Optimizer", layout="wide")
st.title("Portfolio Selection")

# --- Stock Picker ---
selected_tickers = render_stock_picker(SP500_TICKERS)

# --- Stock Analysis ---
if len(selected_tickers) >= 2:
    if st.button("Analyze Selected Stocks"):
        with st.spinner("Analyzing stocks..."):
            try:
                analysis = analyze_stocks(selected_tickers)

                df = pd.DataFrame([
                    {
                        "Ticker": a.ticker,
                        "Price": f"${a.current_price:,.2f}",
                        "Annual Return": f"{a.annualized_return * 100:.1f}%",
                        "Volatility": f"{a.annualized_volatility * 100:.1f}%",
                        "Sharpe": f"{a.sharpe_ratio:.2f}",
                        "Max Drawdown": f"{a.max_drawdown * 100:.1f}%",
                        "Beta": f"{a.beta:.2f}",
                        "52W High": f"${a.high_52w:,.2f}",
                        "52W Low": f"${a.low_52w:,.2f}",
                    }
                    for a in analysis
                ])
                st.dataframe(df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")

# --- Risk Profile ---
risk_profile = render_risk_slider()

st.markdown("---")

# --- Investment Amount ---
st.subheader("Investment Amount")
investment = st.number_input(
    "How much do you want to invest (USD)?",
    min_value=100.0,
    max_value=10_000_000.0,
    value=10_000.0,
    step=1000.0,
    format="%.2f",
)

# --- Method ---
st.subheader("Optimization Method")
method = st.radio(
    "Select the method:",
    options=["markowitz", "genetic", "both"],
    format_func=lambda x: {
        "markowitz": "Markowitz (Mean-Variance)",
        "genetic": "Genetic Algorithm",
        "both": "Compare Both",
    }[x],
    horizontal=True,
)

st.markdown("---")

# --- Optimize Button ---
if st.button("Optimize Portfolio", type="primary", use_container_width=True):
    if len(selected_tickers) < 2:
        st.error("Select at least 2 stocks to continue.")
    else:
        with st.spinner("Downloading data and optimizing... This may take a few seconds."):
            try:
                req = OptimizeRequest(
                    tickers=selected_tickers,
                    risk_profile=risk_profile,
                    investment_amount=investment,
                    method=method,
                )
                result = run_optimization(req)

                # Convert to dict(s) for session state compatibility
                if isinstance(result, list):
                    data = [r.model_dump() for r in result]
                else:
                    data = result.model_dump()

                # Store results in session state
                st.session_state["optimization_result"] = data
                st.session_state["selected_tickers"] = selected_tickers
                st.session_state["investment_amount"] = investment
                st.session_state["risk_profile"] = risk_profile
                st.session_state["method"] = method

                st.success("Optimization complete. Go to the Results page to view the analysis.")
                st.balloons()

            except Exception as e:
                st.error(f"Unexpected error: {e}")
