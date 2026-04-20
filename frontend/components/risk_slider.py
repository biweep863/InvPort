"""Risk appetite selector component."""

import streamlit as st

RISK_OPTIONS = {
    "Low (Conservative)": "bajo",
    "Medium (Balanced)": "medio",
    "High (Aggressive)": "alto",
}

RISK_DESCRIPTIONS = {
    "bajo": "Prioritizes capital preservation. Lower expected return but lower risk of losses.",
    "medio": "Balance between growth and safety. Accepts moderate volatility for better returns.",
    "alto": "Seeks maximum growth. Accepts high volatility and risk of significant temporary losses.",
}


def render_risk_slider() -> str:
    """Render risk appetite selector. Returns 'bajo', 'medio', or 'alto'."""
    st.subheader("Risk Profile")

    selected_label = st.select_slider(
        "What is your risk appetite?",
        options=list(RISK_OPTIONS.keys()),
        value="Medium (Balanced)",
    )

    risk_key = RISK_OPTIONS[selected_label]
    st.info(RISK_DESCRIPTIONS[risk_key])
    return risk_key
