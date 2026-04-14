"""Stock picker component for Streamlit."""

import streamlit as st

POPULAR_GROUPS = {
    "🏆 FAANG+": ["AAPL", "AMZN", "META", "NFLX", "GOOGL", "MSFT"],
    "💻 Tech": ["NVDA", "AMD", "INTC", "ADBE", "CRM", "NOW"],
    "🏦 Finanzas": ["JPM", "V", "MA", "GS", "BLK"],
    "🏥 Salud": ["JNJ", "UNH", "ABBV", "MRK", "LLY", "AMGN"],
    "🛒 Consumo": ["WMT", "COST", "PG", "KO", "PEP", "MCD", "SBUX"],
}


def render_stock_picker(available_tickers: dict[str, str]) -> list[str]:
    """Render stock picker with quick-select groups and multiselect."""
    st.subheader("📊 Selecciona tus Acciones")

    # Quick select groups
    st.write("**Selección rápida por sector:**")
    cols = st.columns(len(POPULAR_GROUPS))
    for col, (group_name, tickers) in zip(cols, POPULAR_GROUPS.items()):
        with col:
            if st.button(group_name, use_container_width=True):
                st.session_state["selected_tickers"] = tickers

    # Manual multiselect
    options = [f"{t} - {n}" for t, n in available_tickers.items()]
    default = st.session_state.get("selected_tickers", [])
    default_options = [f"{t} - {available_tickers[t]}" for t in default if t in available_tickers]

    selected = st.multiselect(
        "Selecciona entre 2 y 15 acciones del S&P 500:",
        options=options,
        default=default_options,
        max_selections=15,
    )

    # Extract ticker symbols
    tickers = [s.split(" - ")[0] for s in selected]
    st.session_state["selected_tickers"] = tickers
    return tickers
