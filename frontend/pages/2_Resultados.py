"""Page 2: Optimization results dashboard."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import pandas as pd
import numpy as np

from InvPort.backend.services.market_data import fetch_historical, compute_returns
from InvPort.frontend.components.charts import (
    allocation_pie_chart,
    efficient_frontier_chart,
    correlation_heatmap,
)

st.set_page_config(page_title="Resultados - Optimizador", page_icon="📈", layout="wide")
st.title("📈 Resultados de Optimización")

# Check for results
if "optimization_result" not in st.session_state:
    st.warning("⚠️ No hay resultados aún. Ve a la página **Selección** y ejecuta una optimización primero.")
    st.stop()

data = st.session_state["optimization_result"]
investment = st.session_state.get("investment_amount", 10000)

# Handle both single result and comparison
if isinstance(data, list):
    results = data
else:
    results = [data]

for idx, result in enumerate(results):
    if len(results) > 1:
        st.markdown(f"### Método: {'Markowitz' if result['method'] == 'markowitz' else 'Algoritmo Genético'}")

    # --- Summary Metrics ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Retorno Esperado Anual",
            f"{result['portfolio_return'] * 100:.2f}%",
        )
    with col2:
        st.metric(
            "Volatilidad Anual",
            f"{result['portfolio_volatility'] * 100:.2f}%",
        )
    with col3:
        st.metric(
            "Ratio de Sharpe",
            f"{result['sharpe_ratio']:.3f}",
        )

    st.markdown("---")

    # --- Allocation ---
    col_pie, col_table = st.columns([1, 1])

    allocations = result["allocations"]

    with col_pie:
        fig_pie = allocation_pie_chart(allocations)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_table:
        st.subheader("📋 Detalle de Asignación")
        df = pd.DataFrame([
            {
                "Ticker": a["ticker"],
                "Empresa": a["company_name"],
                "Peso (%)": f"{a['weight'] * 100:.2f}",
                "Monto (USD)": f"${a['amount']:,.2f}",
                "Retorno Ind. (%)": f"{a['expected_return'] * 100:.2f}",
            }
            for a in allocations if a["weight"] > 0.001
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

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
st.subheader("🔥 Matriz de Correlación")
tickers = st.session_state.get("selected_tickers", [])
if tickers:
    with st.spinner("Calculando correlaciones..."):
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
            "Empresa": a["company_name"],
            "Peso": a["weight"],
            "Monto_USD": a["amount"],
        }
        for a in main_result["allocations"] if a["weight"] > 0.001
    ])
    csv = export_data.to_csv(index=False)
    st.download_button(
        "📥 Descargar Asignación (CSV)",
        data=csv,
        file_name="portfolio_allocation.csv",
        mime="text/csv",
    )
