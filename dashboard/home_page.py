"""
Home page content for the RetentIQ / 404_NotFound dashboard.
"""
import sys
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parents[1])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from dashboard.components.metrics import inject_custom_css, inject_sidebar_brand

st.set_page_config(
    page_title="404_NotFound — Data for Impact 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main .block-container { padding-top: 1rem; }

    /* ── Hero ──────────────────────────────────────────────── */
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
    .hero-badges { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
    .badge {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 999px;
        letter-spacing: 0.3px;
    }
    .badge-blue  { background:#dbeafe; color:#1d4ed8; }
    .badge-green { background:#dcfce7; color:#166534; }
    .badge-purple{ background:#ede9fe; color:#6d28d9; }
    .badge-amber { background:#fef3c7; color:#92400e; }

    /* ── Nav Cards ──────────────────────────────────────────── */
    .nav-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        margin: 8px 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .nav-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.09);
    }
    .nav-card h3 {
        margin: 0 0 6px 0;
        font-size: 1.0rem;
        color: #1e293b;
        font-weight: 600;
    }
    .nav-card p { margin: 0; font-size: 0.85rem; color: #64748b; }
    .nav-card .card-tag {
        display: inline-block;
        font-size: 0.7rem;
        padding: 2px 7px;
        border-radius: 4px;
        margin-bottom: 6px;
        font-weight: 600;
    }
    .tag-foundation { background:#ede9fe; color:#6d28d9; }
    .tag-behavior   { background:#dbeafe; color:#1d4ed8; }
    .tag-risk       { background:#fef2f2; color:#991b1b; }
    .tag-action     { background:#dcfce7; color:#166534; }

    /* ── Research Reference Box ─────────────────────────────── */
    .research-box {
        background: #fafafa;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 8px 0;
    }
    .research-box h4 { margin: 0 0 10px 0; color: #1e293b; font-size: 0.95rem; }
    .research-cite {
        font-size: 0.82rem;
        color: #475569;
        padding: 5px 0;
        border-bottom: 1px solid #f1f5f9;
        line-height: 1.5;
    }
    .research-cite:last-child { border-bottom: none; }
    .research-cite strong { color: #1e40af; }
    .research-cite a { color: #1e40af; text-decoration: underline dotted; }
    .research-cite a:hover { color: #1d4ed8; text-decoration: underline; }
    .research-ref-box a { color: #3730a3; text-decoration: underline dotted; }
    .research-ref-box a:hover { color: #4f46e5; text-decoration: underline; }
    </style>
    """,
    unsafe_allow_html=True,
)

inject_custom_css()
inject_sidebar_brand()

# ── Hero ─────────────────────────────────────────────────────────
st.markdown('<h1 class="hero-title">Data for Impact 2026</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">Team 404_NotFound · Phân tích toàn diện khách hàng: B2B/B2C Segmentation · Churn Prediction · Win-back Strategy</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '''<div class="hero-badges">
        <span class="badge badge-blue">Online Retail Dataset · 5,581 customers</span>
        <span class="badge badge-green">Random Forest · Recall-optimized</span>
        <span class="badge badge-purple">B2B / B2C Dual-track</span>
        <span class="badge badge-amber">Team 404_NotFound</span>
    </div>''',
    unsafe_allow_html=True,
)
st.markdown("---")

# ── Navigation Cards ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        '''<div class="nav-card">
        <span class="card-tag tag-foundation">Foundation</span>
        <h3>1. Executive Overview</h3>
        <p>KPIs tổng quan, Revenue trend, Retention Rate, phân bố RFM & B2B/B2C</p>
        </div>''',
        unsafe_allow_html=True,
    )
    st.markdown(
        '''<div class="nav-card">
        <span class="card-tag tag-foundation">Foundation</span>
        <h3>2. B2B / B2C Segmentation</h3>
        <p>Phân tích nền tảng hai nhóm khách hàng, behavior segments, churn risk heatmap</p>
        </div>''',
        unsafe_allow_html=True,
    )
    st.markdown(
        '''<div class="nav-card">
        <span class="card-tag tag-behavior">Behavior</span>
        <h3>3. Purchasing Behavior</h3>
        <p>Xu hướng doanh thu, AOV, Top Products, phân khúc RFM Segments</p>
        </div>''',
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        '''<div class="nav-card">
        <span class="card-tag tag-behavior">Behavior</span>
        <h3>4. Product Recommendation</h3>
        <p>Hồ sơ khách hàng, Cross-sell/Up-sell scoring, category affinity</p>
        </div>''',
        unsafe_allow_html=True,
    )
    st.markdown(
        '''<div class="nav-card">
        <span class="card-tag tag-risk">At-Risk</span>
        <h3>5. At-Risk Identification</h3>
        <p>Churn prediction ML + Rule-based, cảnh báo sớm, phân bố xác suất rời bỏ</p>
        </div>''',
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        '''<div class="nav-card">
        <span class="card-tag tag-risk">At-Risk</span>
        <h3>6. At-Risk Deep Dive</h3>
        <p>Frequency/Spend decline, purchase cycle gaps, return behavior analysis</p>
        </div>''',
        unsafe_allow_html=True,
    )
    st.markdown(
        '''<div class="nav-card">
        <span class="card-tag tag-action">Action</span>
        <h3>7. Win-back Strategy</h3>
        <p>Chiến dịch P1/P2/P3, B2B vs B2C playbook riêng, ROI estimation</p>
        </div>''',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Project Info + Research Context ──────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Về dự án")
    st.markdown(
        """
        - **Đội thi**: 404_NotFound — Data for Impact 2026
        - **Dữ liệu**: Online Retail II (UCI ML Repository, 2009–2011)
        - **Model**: Random Forest Calibrated (Recall-optimized, threshold tuned)
        - **Segmentation**: Rule-based B2B/B2C + K-Means behavioral clustering
        - **Framework**: Streamlit · Plotly · scikit-learn · pandas
        """
    )
    st.markdown("### Phương pháp phân tích")
    st.markdown(
        """
        - **Feature Engineering**: RFM + Purchase-cycle + Composite scores
        - **B2B/B2C Split**: Signal-based threshold classification (4 signals, ≥2 → B2B)
        - **Prediction**: Churn label từ 60-day inactivity window
        - **Evaluation**: Recall · Precision · F1 · ROC-AUC · PR-AUC · Brier Score
        """
    )

with col2:
    st.markdown("### Nghiên cứu học thuật tham khảo")
    st.markdown(
        '''<div class="research-box">
        <h4>Nền tảng lý thuyết</h4>
        <div class="research-cite"><strong><a href="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10570772/" target="_blank">Sun et al. (2023) — Heliyon / PMC</a>:</strong> RFM + ML outperforms single-method approaches cho noncontractual churn prediction trong e-commerce. Đây là foundation của pipeline dự án.</div>
        <div class="research-cite"><strong><a href="https://hbr.org/2014/10/the-value-of-keeping-the-right-customers" target="_blank">Reichheld (2001) — Bain & Company / HBR</a>:</strong> Tăng 5% retention → tăng 25–95% lợi nhuận. B2B retention rate trung bình 82–90%, cao hơn B2C (74%).</div>
        <div class="research-cite"><strong><a href="https://link.springer.com/article/10.1007/s11747-016-0488-7" target="_blank">Kumar & Reinartz (2016) — JAMS</a>:</strong> RFM + CLV là framework CRM cốt lõi cho phân loại ưu tiên khách hàng.</div>
        <div class="research-cite"><strong><a href="https://www.sciencedirect.com/science/article/abs/pii/S0019850113001600" target="_blank">Tamaddoni et al. (2014) — Industrial Marketing Mgmt</a>:</strong> Data-driven churn prediction outperforms managerial heuristics trong B2B e-commerce.</div>
        <div class="research-cite"><strong><a href="https://rivo.io/resources/customer-retention-statistics" target="_blank">Rivo (2026) — Industry Report</a>:</strong> B2B churn chủ yếu do poor customer service (50% switched vendors), không phải sản phẩm. B2C churn do lack of personalization.</div>
        <div class="research-cite"><strong><a href="https://sarasanalytics.com/blog/customer-retention-dashboard" target="_blank">Saras Analytics (2026)</a>:</strong> Best-practice retention dashboard gồm 5 loại: Cohort, LTV, Repeat Purchase, Segmentation, Marketing Influence.</div>
        </div>''',
        unsafe_allow_html=True,
    )

st.caption("Sử dụng sidebar bên trái để điều hướng giữa các trang phân tích.")
