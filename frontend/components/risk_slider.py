"""Risk appetite selector component."""

import streamlit as st

RISK_OPTIONS = {
    "🟢 Bajo (Conservador)": "bajo",
    "🟡 Medio (Balanceado)": "medio",
    "🔴 Alto (Agresivo)": "alto",
}

RISK_DESCRIPTIONS = {
    "bajo": "Prioriza la preservación del capital. Menor retorno esperado pero menor riesgo de pérdidas.",
    "medio": "Balance entre crecimiento y seguridad. Acepta volatilidad moderada por mejores retornos.",
    "alto": "Busca máximo crecimiento. Acepta alta volatilidad y riesgo de pérdidas temporales significativas.",
}


def render_risk_slider() -> str:
    """Render risk appetite selector. Returns 'bajo', 'medio', or 'alto'."""
    st.subheader("🎯 Perfil de Riesgo")

    selected_label = st.select_slider(
        "¿Cuál es tu apetito de riesgo?",
        options=list(RISK_OPTIONS.keys()),
        value="🟡 Medio (Balanceado)",
    )

    risk_key = RISK_OPTIONS[selected_label]
    st.info(RISK_DESCRIPTIONS[risk_key])
    return risk_key
