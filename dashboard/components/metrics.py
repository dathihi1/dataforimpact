"""Reusable KPI metric card helpers with light theme styling."""
from __future__ import annotations

import streamlit as st


def inject_custom_css() -> None:
    """Inject custom CSS — light palette, subtle shadows, clean typography."""
    st.markdown(
        """
        <style>
        /* ── Global ──────────────────────────────────────────── */
        .main .block-container { padding-top: 1rem; }

        /* ── Metric Cards ────────────────────────────────────── */
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.82rem !important;
            color: #64748b !important;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            font-weight: 500 !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.7rem !important;
            font-weight: 700 !important;
            color: #1e293b !important;
        }
        [data-testid="stMetricDelta"] > div {
            font-size: 0.8rem !important;
        }

        /* ── Insight Boxes ───────────────────────────────────── */
        .insight-box {
            background: #f0f7ff;
            border-left: 4px solid #3b82f6;
            border-radius: 6px;
            padding: 14px 18px;
            margin: 12px 0;
            font-size: 0.93rem;
            line-height: 1.65;
            color: #334155;
        }
        .insight-box strong { color: #1e40af; }
        .insight-box .ref {
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 8px;
            font-style: italic;
        }

        .warning-box {
            background: #fffbeb;
            border-left: 4px solid #f59e0b;
            border-radius: 6px;
            padding: 14px 18px;
            margin: 12px 0;
            color: #334155;
        }
        .warning-box strong { color: #92400e; }

        .danger-box {
            background: #fef2f2;
            border-left: 4px solid #ef4444;
            border-radius: 6px;
            padding: 14px 18px;
            margin: 12px 0;
            color: #334155;
        }
        .danger-box strong { color: #991b1b; }

        .success-box {
            background: #f0fdf4;
            border-left: 4px solid #22c55e;
            border-radius: 6px;
            padding: 14px 18px;
            margin: 12px 0;
            color: #334155;
        }
        .success-box strong { color: #166534; }

        /* ── Section headers ─────────────────────────────────── */
        .section-header {
            font-size: 1.15rem;
            font-weight: 600;
            color: #1e293b;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
            margin: 28px 0 16px 0;
        }

        /* ── DataFrames ──────────────────────────────────────── */
        .stDataFrame { border-radius: 8px; overflow: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def insight_box(text: str, ref: str = "") -> None:
    """Render a styled insight/research callout box."""
    ref_html = f'<div class="ref">{ref}</div>' if ref else ""
    st.markdown(f'<div class="insight-box">{text}{ref_html}</div>', unsafe_allow_html=True)


def warning_box(text: str) -> None:
    """Render a styled warning callout box."""
    st.markdown(f'<div class="warning-box">{text}</div>', unsafe_allow_html=True)


def danger_box(text: str) -> None:
    """Render a styled danger callout box."""
    st.markdown(f'<div class="danger-box">{text}</div>', unsafe_allow_html=True)


def success_box(text: str) -> None:
    """Render a styled success callout box."""
    st.markdown(f'<div class="success-box">{text}</div>', unsafe_allow_html=True)


def section_header(text: str) -> None:
    """Render a styled section header (no emoji)."""
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def metric_card(
    label: str,
    value: str,
    delta: str | None = None,
    delta_color: str = "normal",
) -> None:
    """Render a styled metric card."""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def metric_row(metrics: list[dict], columns: int | None = None) -> None:
    """Render a row of metric cards.

    Parameters
    ----------
    metrics : list[dict]
        Each dict should have keys ``label``, ``value``,
        and optionally ``delta`` and ``delta_color``.
    columns : int, optional
        Number of columns. Defaults to ``len(metrics)``.
    """
    n = columns or len(metrics)
    cols = st.columns(n)
    for col, m in zip(cols, metrics):
        with col:
            metric_card(**m)
