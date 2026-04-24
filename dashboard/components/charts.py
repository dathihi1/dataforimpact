"""Shared chart helpers using Plotly — light theme."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from dashboard.utils.config import COLORS, CHART_TEMPLATE, CHART_COLORS


_LAYOUT_DEFAULTS = dict(
    template=CHART_TEMPLATE,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#334155"),
)


def line_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color: str | None = None,
    height: int = 400,
) -> go.Figure:
    fig = px.line(df, x=x, y=y, color=color, title=title,
                  color_discrete_sequence=CHART_COLORS)
    fig.update_layout(height=height, **_LAYOUT_DEFAULTS)
    return fig


def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color: str | None = None,
    orientation: str = "v",
    height: int = 400,
) -> go.Figure:
    fig = px.bar(
        df, x=x, y=y, color=color, title=title,
        orientation=orientation,
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_layout(height=height, **_LAYOUT_DEFAULTS)
    return fig


def pie_chart(
    df: pd.DataFrame,
    values: str,
    names: str,
    title: str = "",
    color_map: dict | None = None,
    height: int = 400,
) -> go.Figure:
    fig = px.pie(
        df, values=values, names=names, title=title,
        color=names,
        color_discrete_map=color_map or {},
        hole=0.4,
    )
    fig.update_layout(height=height, **_LAYOUT_DEFAULTS)
    return fig


def histogram_chart(
    df: pd.DataFrame,
    x: str,
    title: str = "",
    nbins: int = 50,
    color: str | None = None,
    height: int = 400,
) -> go.Figure:
    fig = px.histogram(
        df, x=x, nbins=nbins, color=color, title=title,
        marginal="box",
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_layout(height=height, **_LAYOUT_DEFAULTS)
    return fig
