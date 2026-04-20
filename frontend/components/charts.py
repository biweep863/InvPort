"""Plotly chart builders for the portfolio optimizer."""

import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd


def allocation_pie_chart(allocations: list[dict]) -> go.Figure:
    """Create a donut chart of portfolio allocation."""
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
        title="Portfolio Distribution",
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

    vols = [p["volatility"] * 100 for p in frontier]
    rets = [p["expected_return"] * 100 for p in frontier]
    fig.add_trace(go.Scatter(
        x=vols, y=rets,
        mode="lines",
        name="Efficient Frontier",
        line=dict(color="royalblue", width=2),
    ))

    fig.add_trace(go.Scatter(
        x=[optimal_point["volatility"] * 100],
        y=[optimal_point["expected_return"] * 100],
        mode="markers",
        name=f"Optimal ({optimal_point.get('method', 'markowitz')})",
        marker=dict(color="gold", size=16, symbol="star", line=dict(width=2, color="black")),
    ))

    if comparison_point:
        fig.add_trace(go.Scatter(
            x=[comparison_point["volatility"] * 100],
            y=[comparison_point["expected_return"] * 100],
            mode="markers",
            name=f"Optimal ({comparison_point.get('method', 'genetic')})",
            marker=dict(color="red", size=14, symbol="diamond", line=dict(width=2, color="black")),
        ))

    fig.update_layout(
        title="Markowitz Efficient Frontier",
        xaxis_title="Annual Volatility (%)",
        yaxis_title="Expected Annual Return (%)",
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
        title="Correlation Matrix",
        height=500,
        template="plotly_white",
    )
    return fig


def monte_carlo_fan_chart(percentiles: dict, days: int, investment: float) -> go.Figure:
    """Create a fan chart showing Monte Carlo simulation percentile bands."""
    x = list(range(days + 1))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x + x[::-1],
        y=percentiles["p95"] + percentiles["p5"][::-1],
        fill="toself",
        fillcolor="rgba(68, 114, 196, 0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Range 5%-95%",
    ))

    fig.add_trace(go.Scatter(
        x=x + x[::-1],
        y=percentiles["p75"] + percentiles["p25"][::-1],
        fill="toself",
        fillcolor="rgba(68, 114, 196, 0.3)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Range 25%-75%",
    ))

    fig.add_trace(go.Scatter(
        x=x,
        y=percentiles["p50"],
        mode="lines",
        name="Median (50%)",
        line=dict(color="royalblue", width=2),
    ))

    fig.add_hline(
        y=investment,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Initial Investment: ${investment:,.0f}",
    )

    fig.update_layout(
        title="Monte Carlo Simulation - Portfolio Evolution",
        xaxis_title="Days",
        yaxis_title="Portfolio Value (USD)",
        height=500,
        template="plotly_white",
    )
    return fig


def risk_contribution_chart(tickers: list[str], contributions: list[float]) -> go.Figure:
    """Bar chart showing each stock's contribution to portfolio risk."""
    # Filter out near-zero contributions
    data = [(t, c) for t, c in zip(tickers, contributions) if abs(c) > 0.001]
    data.sort(key=lambda x: x[1], reverse=True)

    fig = go.Figure(data=[go.Bar(
        x=[d[0] for d in data],
        y=[d[1] * 100 for d in data],
        marker_color=["#e74c3c" if d[1] > 0.15 else "#3498db" for d in data],
    )])
    fig.update_layout(
        title="Risk Contribution by Stock",
        xaxis_title="Stock",
        yaxis_title="Risk Contribution (%)",
        height=400,
        template="plotly_white",
    )
    return fig


def backtest_chart(dates: list[str], portfolio_values: list[float], benchmark_values: list[float]) -> go.Figure:
    """Line chart comparing portfolio vs benchmark performance."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates, y=portfolio_values,
        mode="lines",
        name="Portfolio",
        line=dict(color="royalblue", width=2),
    ))

    fig.add_trace(go.Scatter(
        x=dates, y=benchmark_values,
        mode="lines",
        name="SPY (Benchmark)",
        line=dict(color="gray", width=1.5, dash="dot"),
    ))

    fig.update_layout(
        title="Historical Performance: Portfolio vs SPY",
        xaxis_title="Date",
        yaxis_title="Value (USD)",
        height=500,
        template="plotly_white",
        hovermode="x unified",
    )
    return fig


def drawdown_chart(dates: list[str], drawdown_series: list[float]) -> go.Figure:
    """Area chart showing portfolio drawdown over time."""
    dd_pct = [-d * 100 for d in drawdown_series]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=dd_pct,
        fill="tozeroy",
        fillcolor="rgba(231, 76, 60, 0.3)",
        line=dict(color="#e74c3c", width=1),
        name="Drawdown",
    ))

    fig.update_layout(
        title="Historical Drawdown",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        height=350,
        template="plotly_white",
    )
    return fig
