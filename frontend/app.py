"""Streamlit main entry point for the Portfolio Optimizer."""

import streamlit as st

st.set_page_config(
    page_title="S&P 500 Portfolio Optimizer",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Portfolio Optimizer")
st.sidebar.markdown("""
Smart tool to optimize your investment portfolio
using S&P 500 stocks.

**Technologies:**
- Markowitz Theory
- Genetic Algorithm
- Monte Carlo Simulation
- Real-time data (Yahoo Finance)
""")

st.sidebar.markdown("---")
st.sidebar.markdown("Navigate using the pages in the sidebar menu.")

st.title("Smart Investment Portfolio Optimizer")
st.markdown("### S&P 500")

st.markdown("""
Welcome to the **Portfolio Optimizer**. This tool helps you find
the optimal asset combination that maximizes your expected return while minimizing risk.

#### How does it work?
1. **Select** the stocks you're interested in from the S&P 500
2. **Define** your risk profile (conservative, balanced, or aggressive)
3. **Get** the optimal distribution for your investment
4. **Simulate** future scenarios with Monte Carlo

#### Get started by navigating to the **"1 - Selection"** page in the sidebar menu.
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Available Stocks", "100+")
with col2:
    st.metric("Optimization Methods", "2")
with col3:
    st.metric("Data", "Real-Time")
