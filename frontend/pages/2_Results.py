"""Page 2: Optimization results dashboard."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import streamlit as st
import pandas as pd
import numpy as np

from InvPort.backend.services.market_data import fetch_historical, compute_returns
from InvPort.frontend.components.charts import (
    allocation_pie_chart,
    efficient_frontier_chart,
    correlation_heatmap,
    risk_contribution_chart,
)

st.set_page_config(page_title="Results - Optimizer", layout="wide")
st.title("Optimization Results")

if "optimization_result" not in st.session_state:
    st.warning("No results yet. Go to the Selection page and run an optimization first.")
    st.stop()

data = st.session_state["optimization_result"]
investment = st.session_state.get("investment_amount", 10000)

if isinstance(data, list):
    results = data
else:
    results = [data]

for idx, result in enumerate(results):
    if len(results) > 1:
        st.markdown(f"### Method: {'Markowitz' if result['method'] == 'markowitz' else 'Genetic Algorithm'}")

    # --- Primary Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Expected Annual Return", f"{result['portfolio_return'] * 100:.2f}%")
    with col2:
        st.metric("Annual Volatility", f"{result['portfolio_volatility'] * 100:.2f}%")
    with col3:
        st.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.3f}")
    with col4:
        metrics = result.get("metrics")
        if metrics:
            st.metric("Sortino Ratio", f"{metrics['sortino_ratio']:.3f}")

    # --- Extended Metrics ---
    if metrics:
        st.markdown("---")
        st.subheader("Advanced Metrics")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Max Drawdown", f"{metrics['max_drawdown'] * 100:.2f}%")
            st.caption("Largest drop from a historical peak")
        with col2:
            st.metric("CVaR 95%", f"{metrics['cvar_95'] * 100:.2f}%")
            st.caption("Expected loss in the worst 5% of days")
        with col3:
            st.metric("Beta (vs SPY)", f"{metrics['beta']:.3f}")
            st.caption("Market sensitivity (1.0 = same as market)")
        with col4:
            st.metric("Alpha (Jensen)", f"{metrics['alpha'] * 100:.2f}%")
            st.caption("Return above what CAPM predicts")

        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("Calmar Ratio", f"{metrics['calmar_ratio']:.3f}")
            st.caption("Return adjusted for max drawdown")
        with col6:
            st.metric("Treynor Ratio", f"{metrics['treynor_ratio']:.3f}")
            st.caption("Return per unit of systematic risk")
        with col7:
            st.metric("Information Ratio", f"{metrics['information_ratio']:.3f}")
            st.caption("Active return per unit of tracking error")
        with col8:
            pass  # empty column for alignment

    st.markdown("---")

    # --- Allocation ---
    col_pie, col_table = st.columns([1, 1])

    allocations = result["allocations"]

    with col_pie:
        fig_pie = allocation_pie_chart(allocations)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_table:
        st.subheader("Allocation Details")
        df = pd.DataFrame([
            {
                "Ticker": a["ticker"],
                "Company": a["company_name"],
                "Weight (%)": f"{a['weight'] * 100:.2f}",
                "Amount (USD)": f"${a['amount']:,.2f}",
                "Ind. Return (%)": f"{a['expected_return'] * 100:.2f}",
            }
            for a in allocations if a["weight"] > 0.001
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # --- Risk Contributions ---
    if metrics and metrics.get("risk_contributions"):
        st.markdown("---")
        st.subheader("Risk Contribution")
        filtered_alloc = [a for a in allocations if a["weight"] > 0.001]
        rc = metrics["risk_contributions"]
        tickers_rc = [a["ticker"] for a in filtered_alloc]
        rc_filtered = rc[:len(tickers_rc)]
        fig_rc = risk_contribution_chart(tickers_rc, rc_filtered)
        st.plotly_chart(fig_rc, use_container_width=True)

    # --- Efficient Frontier ---
    if result.get("efficient_frontier"):
        st.markdown("---")
        optimal_point = {
            "volatility": result["portfolio_volatility"],
            "expected_return": result["portfolio_return"],
            "method": result["method"],
        }
        comparison = None
        if len(results) > 1 and idx == 0:
            comparison = {
                "volatility": results[1]["portfolio_volatility"],
                "expected_return": results[1]["portfolio_return"],
                "method": results[1]["method"],
            }

        fig_frontier = efficient_frontier_chart(
            result["efficient_frontier"],
            optimal_point,
            comparison,
        )
        st.plotly_chart(fig_frontier, use_container_width=True)

    if len(results) > 1 and idx < len(results) - 1:
        st.markdown("---")
        st.markdown("---")

# --- Correlation Heatmap ---
st.markdown("---")
st.subheader("Correlation Matrix")
tickers = st.session_state.get("selected_tickers", [])
if tickers:
    with st.spinner("Computing correlations..."):
        prices = fetch_historical(tickers)
        returns = compute_returns(prices)
        corr = returns.corr()
        fig_corr = correlation_heatmap(corr)
        st.plotly_chart(fig_corr, use_container_width=True)

# --- Export ---
st.markdown("---")
if results:
    main_result = results[0]
    export_data = pd.DataFrame([
        {
            "Ticker": a["ticker"],
            "Company": a["company_name"],
            "Weight": a["weight"],
            "Amount_USD": a["amount"],
        }
        for a in main_result["allocations"] if a["weight"] > 0.001
    ])
    csv = export_data.to_csv(index=False)
    st.download_button(
        "Download Allocation (CSV)",
        data=csv,
        file_name="portfolio_allocation.csv",
        mime="text/csv",
    )
