"""Streamlit main entry point for the Portfolio Optimizer."""

import streamlit as st

st.set_page_config(
    page_title="Optimizador de Portafolios S&P 500",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Optimizador de Portafolios")
st.sidebar.markdown("""
Herramienta inteligente para optimizar tu portafolio de inversion
usando acciones del S&P 500.

**Tecnologias:**
- Teoria de Markowitz
- Algoritmo Genetico
- Simulacion Monte Carlo
- Datos en tiempo real (Yahoo Finance)
""")

st.sidebar.markdown("---")
st.sidebar.markdown("Navega usando las paginas del menu lateral.")

st.title("Optimizador Inteligente de Portafolios de Inversion")
st.markdown("### S&P 500")

st.markdown("""
Bienvenido al **Optimizador de Portafolios**. Esta herramienta te ayuda a encontrar
la combinacion optima de activos que maximice tu retorno esperado minimizando el riesgo.

#### Como funciona?
1. **Selecciona** las acciones que te interesen del S&P 500
2. **Define** tu perfil de riesgo (conservador, balanceado o agresivo)
3. **Obten** la distribucion optima de tu inversion
4. **Simula** escenarios futuros con Monte Carlo

#### Comienza navegando a la pagina **"1 - Seleccion"** en el menu lateral.
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Acciones Disponibles", "100+")
with col2:
    st.metric("Metodos de Optimizacion", "2")
with col3:
    st.metric("Datos", "Tiempo Real")
