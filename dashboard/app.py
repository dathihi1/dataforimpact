"""
At-Risk Customer Dashboard — 404_NotFound | Data for Impact 2026
=================================================================
Navigation controller.

Usage:
    cd 404_Not_Found
    streamlit run dashboard/app.py
"""
import sys
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parents[1])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from dashboard.components.metrics import inject_custom_css

# Inject global CSS
inject_custom_css()

# ── Style the first nav item as brand header ─────────────────────
st.sidebar.markdown(
    """
    <style>
    /* Ẩn st.logo mặc định nếu còn sót */
    [data-testid="stLogo"] { display: none !important; }

    /* ── Style mục đầu tiên trong sidebar nav thành brand ── */
    /* Container li */
    [data-testid="stSidebarNav"] ul li:first-child {
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 14px !important;
        margin-bottom: 8px !important;
    }
    /* Link chính */
    [data-testid="stSidebarNav"] ul li:first-child a {
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
        padding: 16px 16px 6px 16px !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        line-height: 1.2 !important;
        background: linear-gradient(135deg, rgba(37,99,235,0.06), rgba(99,102,241,0.06)) !important;
        border-radius: 10px !important;
        border-left: 4px solid #3b82f6 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebarNav"] ul li:first-child a:hover {
        background: linear-gradient(135deg, rgba(37,99,235,0.12), rgba(99,102,241,0.12)) !important;
        transform: translateX(2px);
    }
    /* Text bên trong — màu xanh đậm nổi bật */
    [data-testid="stSidebarNav"] ul li:first-child a span,
    [data-testid="stSidebarNav"] ul li:first-child a p {
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: unset !important;
        color: #2563eb !important;
    }
    /* Dòng subtitle "Data for Impact 2026" */
    [data-testid="stSidebarNav"] ul li:first-child a::after {
        content: "Data for Impact 2026";
        display: block !important;
        font-size: 0.72rem !important;
        font-weight: 400 !important;
        color: #94a3b8 !important;
        letter-spacing: 0.3px;
        margin-top: 4px;
        white-space: normal !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

pg = st.navigation(
    [
        st.Page("home_page.py", title="404_NotFound"),
        st.Page("pages/1_Executive_Overview.py",    title="Executive Overview"),
        st.Page("pages/2_B2B_B2C_Segmentation.py", title="B2B / B2C Segmentation"),
        st.Page("pages/3_Purchasing_Behavior.py",   title="Purchasing Behavior"),
        st.Page("pages/4_Product_Recommendation.py",title="Product Recommendation"),
        st.Page("pages/5_AtRisk_Identification.py", title="At-Risk Identification"),
        st.Page("pages/6_AtRisk_DeepDive.py",       title="At-Risk Deep Dive"),
        st.Page("pages/7_Winback_Strategy.py",      title="Win-back Strategy"),
    ]
)
pg.run()
