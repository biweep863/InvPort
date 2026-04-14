"""Plotly chart builders for the portfolio optimizer."""

import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd


def allocation_pie_chart(allocations: list[dict]) -> go.Figure:
    """Create a donut chart of portfolio allocation."""
    # Filter out near-zero allocations
    filtered = [a for a in allocations if a["weight"] > 0.01]
    labels = [f"{a['ticker']} ({a['weight']*100:.1f}%)" for a in filtered]
    values = [a["weight"] for a in filtered]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        textinfo="label+percent",
        marker=dict(colors=px.colors.qualitative.Set2),
    )])
    fig.update_layout(
        title="Distribución del Portafolio",
        showlegend=True,
        height=450,
    )
    return fig


def efficient_frontier_chart(
    frontier: list[dict],
    optimal_point: dict,
    comparison_point: dict | None = None,
) -> go.Figure:
    """Plot the efficient frontier with the optimal portfolio highlighted."""
    fig = go.Figure()

    # Frontier curve
    vols = [p["volatility"] * 100 for p in frontier]
    rets = [p["expected_return"] * 100 for p in frontier]
    fig.add_trace(go.Scatter(
        x=vols, y=rets,
        mode="lines",
        name="Frontera Eficiente",
        line=dict(color="royalblue", width=2),
    ))

    # Optimal point
    fig.add_trace(go.Scatter(
        x=[optimal_point["volatility"] * 100],
        y=[optimal_point["expected_return"] * 100],
        mode="markers",
        name=f"Óptimo ({optimal_point.get('method', 'markowitz')})",
        marker=dict(color="gold", size=16, symbol="star", line=dict(width=2, color="black")),
    ))

    if comparison_point:
        fig.add_trace(go.Scatter(
            x=[comparison_point["volatility"] * 100],
            y=[comparison_point["expected_return"] * 100],
            mode="markers",
            name=f"Óptimo ({comparison_point.get('method', 'genetic')})",
            marker=dict(color="red", size=14, symbol="diamond", line=dict(width=2, color="black")),
        ))

    fig.update_layout(
        title="Frontera Eficiente de Markowitz",
        xaxis_title="Volatilidad Anual (%)",
        yaxis_title="Retorno Esperado Anual (%)",
        height=500,
        template="plotly_white",
    )
    return fig


def correlation_heatmap(correlation_matrix: pd.DataFrame) -> go.Figure:
    """Create a heatmap of stock correlations."""
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns.tolist(),
        y=correlation_matrix.index.tolist(),
        colorscale="RdBu_r",
        zmin=-1, zmax=1,
        text=np.round(correlation_matrix.values, 2),
        texttemplate="%{text}",
        textfont={"size": 10},
    ))
    fig.update_layout(
        title="Matriz de Correlación",
        height=500,
        template="plotly_white",
    )
    return fig


def monte_carlo_fan_chart(percentiles: dict, days: int, investment: float) -> go.Figure:
    """Create a fan chart showing Monte Carlo simulation percentile bands."""
    x = list(range(days + 1))

    fig = go.Figure()

    # 5-95 percentile band
    fig.add_trace(go.Scatter(
        x=x + x[::-1],
        y=percentiles["p95"] + percentiles["p5"][::-1],
        fill="toself",
        fillcolor="rgba(68, 114, 196, 0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Rango 5%-95%",
    ))

    # 25-75 percentile band
    fig.add_trace(go.Scatter(
        x=x + x[::-1],
        y=percentiles["p75"] + percentiles["p25"][::-1],
        fill="toself",
        fillcolor="rgba(68, 114, 196, 0.3)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Rango 25%-75%",
    ))

    # Median line
    fig.add_trace(go.Scatter(
        x=x,
        y=percentiles["p50"],
        mode="lines",
        name="Mediana (50%)",
        line=dict(color="royalblue", width=2),
    ))

    # Initial investment line
    fig.add_hline(
        y=investment,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Inversión Inicial: ${investment:,.0f}",
    )

    fig.update_layout(
        title="Simulación Monte Carlo - Evolución del Portafolio",
        xaxis_title="Días",
        yaxis_title="Valor del Portafolio (USD)",
        height=500,
        template="plotly_white",
    )
    return fig
