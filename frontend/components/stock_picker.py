"""Stock picker component for Streamlit."""

import streamlit as st

POPULAR_GROUPS = {
    "FAANG+": ["AAPL", "AMZN", "META", "NFLX", "GOOGL", "MSFT"],
    "Semiconductors": ["NVDA", "AMD", "INTC", "AVGO", "QCOM", "TXN", "MU"],
    "Software": ["ADBE", "CRM", "NOW", "ORCL", "PANW", "CRWD"],
    "Finance": ["JPM", "GS", "MS", "BAC", "BLK", "AXP"],
    "Payments": ["V", "MA", "PYPL", "SQ"],
    "Healthcare": ["JNJ", "UNH", "LLY", "ABBV", "MRK", "PFE", "AMGN"],
    "Consumer": ["WMT", "COST", "PG", "KO", "PEP", "MCD", "SBUX", "NKE"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
    "Industrial": ["BA", "CAT", "GE", "HON", "DE", "LMT"],
}


def render_stock_picker(available_tickers: dict[str, str]) -> list[str]:
    """Render stock picker with quick-select groups and multiselect."""
    st.subheader("Select Your Stocks")

    def format_option(ticker: str) -> str:
        return f"{ticker} - {available_tickers[ticker]}"

    options_key = "selected_ticker_options"
    tickers_key = "selected_tickers"

    if options_key not in st.session_state:
        initial_tickers = st.session_state.get(tickers_key, [])
        st.session_state[options_key] = [
            format_option(t) for t in initial_tickers if t in available_tickers
        ]

    # Quick select groups
    st.write("**Quick select by sector:**")
    cols = st.columns(len(POPULAR_GROUPS))
    for col, (group_name, tickers) in zip(cols, POPULAR_GROUPS.items()):
        with col:
            if st.button(group_name, use_container_width=True):
                st.session_state[options_key] = [
                    format_option(t) for t in tickers if t in available_tickers
                ]
                st.session_state[tickers_key] = [t for t in tickers if t in available_tickers]

    # Manual multiselect
    selected = st.multiselect(
        "Select between 2 and 15 S&P 500 stocks:",
        options=[format_option(t) for t in available_tickers],
        key=options_key,
        max_selections=15,
    )

    # Extract ticker symbols
    tickers = [s.split(" - ")[0] for s in selected]
    st.session_state[tickers_key] = tickers
    return tickers
