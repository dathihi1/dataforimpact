"""
At-Risk Customer Dashboard
===========================
Main entry point for the Streamlit multi-page dashboard.

Usage:
    cd 404_Not_Found
    streamlit run dashboard/app.py
"""
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

st.set_page_config(
    page_title="At-Risk Customer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main .block-container { padding-top: 1rem; }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #64748b;
        margin-top: 4px;
    }
    .nav-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        margin: 8px 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .nav-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .nav-card h3 {
        margin: 0 0 8px 0;
        font-size: 1.05rem;
        color: #1e293b;
    }
    .nav-card p {
        margin: 0;
        font-size: 0.88rem;
        color: #64748b;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Hero ─────────────────────────────────────────────────────────
st.markdown('<h1 class="hero-title">At-Risk Customer Dashboard</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">Phân tích chuyên sâu khách hàng có nguy cơ rời bỏ — '
    'Powered by Machine Learning & Data-driven Insights</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Navigation Cards ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        '''<div class="nav-card">
        <h3>1. Executive Overview</h3>
        <p>KPIs tổng quan, Retention Rate, phân bố khách hàng, hiệu quả kinh doanh</p>
        </div>''',
        unsafe_allow_html=True,
    )
    st.markdown(
        '''<div class="nav-card">
        <h3>2. Purchasing Behavior</h3>
        <p>Xu hướng doanh thu, AOV, Top Products, phân khúc RFM Segments</p>
        </div>''',
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        '''<div class="nav-card">
        <h3>3. Product Recommendation</h3>
        <p>Hồ sơ khách hàng, Lookalike groups, Cross-sell/Up-sell scoring</p>
        </div>''',
        unsafe_allow_html=True,
    )
    st.markdown(
        '''<div class="nav-card">
        <h3>4. At-Risk Identification</h3>
        <p>Churn prediction, cảnh báo sớm, phân bố xác suất rời bỏ</p>
        </div>''',
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        '''<div class="nav-card">
        <h3>5. At-Risk Deep Dive</h3>
        <p>Frequency/Spend decline, purchase gaps, return behavior</p>
        </div>''',
        unsafe_allow_html=True,
    )
    st.markdown(
        '''<div class="nav-card">
        <h3>6. Win-back Strategy</h3>
        <p>Chiến dịch can thiệp, mức ưu tiên P1/P2/P3, ROI estimation</p>
        </div>''',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Project Info ─────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        ### Về dự án
        - **Dự án**: 404_Not_Found — Data for Impact
        - **Dữ liệu**: Online Retail Dataset (UCI ML Repository)
        - **Model**: Random Forest (Business-value optimized, Calibrated)
        - **Framework**: Streamlit + Plotly + scikit-learn
        """
    )

with col2:
    st.markdown(
        """
        ### Phương pháp
        - **Feature Engineering**: RFM + Cycle-based + Composite scores
        - **Segmentation**: Rule-based + K-Means clustering
        - **Prediction**: Random Forest Classifier
        - **Evaluation**: Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, Brier
        """
    )

st.caption("Sử dụng sidebar bên trái để điều hướng giữa các trang phân tích.")
