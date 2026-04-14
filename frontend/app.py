"""Streamlit main entry point for the Portfolio Optimizer."""

import streamlit as st

st.set_page_config(
    page_title="Optimizador de Portafolios S&P 500",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("📈 Optimizador de Portafolios")
st.sidebar.markdown("""
Herramienta inteligente para optimizar tu portafolio de inversión
usando acciones del S&P 500.

**Tecnologías:**
- Teoría de Markowitz
- Algoritmo Genético
- Simulación Monte Carlo
- Datos en tiempo real (Yahoo Finance)
""")

st.sidebar.markdown("---")
st.sidebar.markdown("Navega usando las páginas del menú lateral ☝️")

st.title("🏠 Optimizador Inteligente de Portafolios de Inversión")
st.markdown("### S&P 500")

st.markdown("""
Bienvenido al **Optimizador de Portafolios**. Esta herramienta te ayuda a encontrar
la combinación óptima de activos que maximice tu retorno esperado minimizando el riesgo.

#### ¿Cómo funciona?
1. **Selecciona** las acciones que te interesen del S&P 500
2. **Define** tu perfil de riesgo (conservador, balanceado o agresivo)
3. **Obtén** la distribución óptima de tu inversión
4. **Simula** escenarios futuros con Monte Carlo

#### Comienza navegando a la página **"1 - Selección"** en el menú lateral.
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Acciones Disponibles", "50+")
with col2:
    st.metric("Métodos de Optimización", "2")
with col3:
    st.metric("Datos", "Tiempo Real")
