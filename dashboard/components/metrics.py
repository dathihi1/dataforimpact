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

        /* ── Research Reference Box ─────────────────────────── */
        .research-ref-box {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #6366f1;
            border-radius: 6px;
            padding: 14px 18px;
            margin: 12px 0;
        }
        .research-ref-box .ref-title {
            font-size: 0.78rem;
            font-weight: 700;
            color: #6366f1;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        .research-ref-box .ref-item {
            font-size: 0.82rem;
            color: #475569;
            padding: 4px 0;
            border-bottom: 1px dotted #e2e8f0;
            line-height: 1.5;
        }
        .research-ref-box .ref-item:last-child { border-bottom: none; }
        .research-ref-box .ref-item strong { color: #3730a3; }

        /* ── Sidebar breadcrumb ──────────────────────────────── */
        [data-testid="stSidebar"] .stMarkdown p {
            font-size: 0.85rem;
        }

        /* ── Sidebar product branding ─────────────────────────────────────── */
        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 4px 14px 4px;
            margin-bottom: 4px;
            border-bottom: 1px solid #e2e8f0;
        }
        .sidebar-brand .brand-name {
            font-size: 1.18rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: #1e293b;
            line-height: 1.1;
        }
        .sidebar-brand .brand-name span {
            color: #3b82f6;
        }
        .sidebar-brand .brand-tagline {
            font-size: 0.68rem;
            color: #94a3b8;
            letter-spacing: 0.3px;
            margin-top: 1px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_sidebar_brand() -> None:
    """Render RetentIQ product branding at top of sidebar.
    Note: Handled centrally in app.py to appear above navigation.
    """
    pass


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


def research_ref_box(title: str, refs: list[tuple[str, str]]) -> None:
    """Render a styled research references box.

    Parameters
    ----------
    title : str
        Section title shown above the references.
    refs : list[tuple[str, str]]
        Each tuple is (citation_label, insight_text).
    """
    items_html = "".join(
        f'<div class="ref-item"><strong>{label}:</strong> {text}</div>'
        for label, text in refs
    )
    st.markdown(
        f'<div class="research-ref-box">'
        f'<div class="ref-title">{title}</div>'
        f'{items_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


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
