"""Page 6 – Win-back Strategy.

Chiến lược can thiệp cho khách hàng at-risk: mức ưu tiên,
gợi ý chiến dịch, xác suất quay lại, ROI estimation.
"""
import sys
from pathlib import Path
_ROOT = str(Path(__file__).resolve().parents[2])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from dashboard.utils.data_loader import load_winback, load_customer_360
from dashboard.components.metrics import (
    metric_row, inject_custom_css, insight_box, success_box,
    section_header,
)
from dashboard.components.charts import pie_chart
from dashboard.components.filters import priority_filter
from dashboard.utils.config import PRIORITY_COLORS, SEGMENT_COLORS

st.set_page_config(page_title="Win-back Strategy", page_icon="📊", layout="wide")
inject_custom_css()

st.markdown("# Win-back Strategy for At-Risk Customers")
st.caption("Chiến lược can thiệp, mức ưu tiên, và xác suất khách hàng quay lại mua sắm")

# ── Data ─────────────────────────────────────────────────────────
wb = load_winback()
df = load_customer_360()

# ── Sidebar Filters ──────────────────────────────────────────────
with st.sidebar:
    st.subheader("Bộ lọc Win-back")
    filtered_wb = priority_filter(wb, key="wb_priority")

# ══════════════════════════════════════════════════════════════════
#  Campaign Overview
# ══════════════════════════════════════════════════════════════════
section_header("Tổng quan Chiến dịch Win-back")

total_at_risk = len(filtered_wb)
p1_count = int((filtered_wb["intervention_priority"] == "P1 - Urgent Win-back").sum())
p2_count = int((filtered_wb["intervention_priority"] == "P2 - Moderate Win-back").sum())
p3_count = int((filtered_wb["intervention_priority"] == "P3 - Light Touch").sum())

metric_row([
    {"label": "Tổng At-Risk", "value": f"{total_at_risk:,}"},
    {"label": "P1 - Urgent", "value": f"{p1_count:,}"},
    {"label": "P2 - Moderate", "value": f"{p2_count:,}"},
    {"label": "P3 - Light Touch", "value": f"{p3_count:,}"},
])

insight_box(
    f"Tổng cộng <strong>{total_at_risk:,}</strong> khách hàng cần can thiệp. "
    f"Trong đó <strong>{p1_count:,}</strong> khách P1 (Urgent) cần hành động ngay — "
    f"đây là nhóm có xác suất churn > 80% nhưng vẫn có thể cứu vãn nếu can thiệp kịp thời.",
    ref="Bain & Company: Chiến dịch win-back hiệu quả có thể recover 20–40% "
    "khách hàng at-risk nếu can thiệp trong 30 ngày đầu tiên."
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Campaign Strategy Matrix
# ══════════════════════════════════════════════════════════════════
section_header("Ma trận chiến lược can thiệp")

st.markdown(
    """
    <table style="width:100%; border-collapse:collapse; font-size:0.93rem;">
    <thead>
        <tr style="background:#f8fafc; color:#334155; font-weight:600;">
            <th style="padding:12px; border:1px solid #e2e8f0; text-align:left;">Mức ưu tiên</th>
            <th style="padding:12px; border:1px solid #e2e8f0; text-align:left;">Churn Prob</th>
            <th style="padding:12px; border:1px solid #e2e8f0; text-align:left;">Hành động</th>
            <th style="padding:12px; border:1px solid #e2e8f0; text-align:left;">Kênh</th>
            <th style="padding:12px; border:1px solid #e2e8f0; text-align:left;">Ưu đãi</th>
            <th style="padding:12px; border:1px solid #e2e8f0; text-align:left;">Xác suất quay lại*</th>
        </tr>
    </thead>
    <tbody>
        <tr style="background:#fef2f2;">
            <td style="padding:10px; border:1px solid #e2e8f0;"><strong>P1 - Urgent</strong></td>
            <td style="padding:10px; border:1px solid #e2e8f0;">≥ 80%</td>
            <td style="padding:10px; border:1px solid #e2e8f0;">Email chăm sóc + Voucher mạnh (20-30%)</td>
            <td style="padding:10px; border:1px solid #e2e8f0;">Email + SMS + Retargeting</td>
            <td style="padding:10px; border:1px solid #e2e8f0;">Voucher 20–30%, Free shipping, Gift</td>
            <td style="padding:10px; border:1px solid #e2e8f0; color:#ef4444;">10–20%</td>
        </tr>
        <tr style="background:#fffbeb;">
            <td style="padding:10px; border:1px solid #e2e8f0;"><strong>P2 - Moderate</strong></td>
            <td style="padding:10px; border:1px solid #e2e8f0;">50–80%</td>
            <td style="padding:10px; border:1px solid #e2e8f0;">Email nhắc nhở + Voucher nhẹ (10-15%)</td>
            <td style="padding:10px; border:1px solid #e2e8f0;">Email + Push notification</td>
            <td style="padding:10px; border:1px solid #e2e8f0;">Voucher 10–15%, Sản phẩm phễu</td>
            <td style="padding:10px; border:1px solid #e2e8f0; color:#f59e0b;">25–40%</td>
        </tr>
        <tr style="background:#f0fdf4;">
            <td style="padding:10px; border:1px solid #e2e8f0;"><strong>P3 - Light Touch</strong></td>
            <td style="padding:10px; border:1px solid #e2e8f0;">< 50%</td>
            <td style="padding:10px; border:1px solid #e2e8f0;">Newsletter + Gợi ý sản phẩm mới</td>
            <td style="padding:10px; border:1px solid #e2e8f0;">Email newsletter</td>
            <td style="padding:10px; border:1px solid #e2e8f0;">Sản phẩm mới, Content marketing</td>
            <td style="padding:10px; border:1px solid #e2e8f0; color:#22c55e;">50–70%</td>
        </tr>
    </tbody>
    </table>
    <p style="font-size:0.8rem; color:#64748b; margin-top:8px;">
    * Xác suất quay lại ước tính dựa trên benchmark ngành TMĐT (Retention Science, 2022).
    </p>
    """,
    unsafe_allow_html=True,
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Priority Distribution Charts
# ══════════════════════════════════════════════════════════════════
section_header("Phân bố & Phân tích theo Priority")

col1, col2 = st.columns(2)

with col1:
    priority_counts = (
        filtered_wb.groupby("intervention_priority", as_index=False)
        .agg(count=("Customer ID", "nunique"))
    )
    fig = pie_chart(
        priority_counts, values="count", names="intervention_priority",
        title="Phân bố mức ưu tiên",
        color_map=PRIORITY_COLORS,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.box(
        filtered_wb,
        x="intervention_priority",
        y="churn_probability",
        color="intervention_priority",
        color_discrete_map=PRIORITY_COLORS,
        title="Churn Probability theo Priority",
        points="outliers",
    )
    fig.update_layout(
        height=400, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  RFM Segment Breakdown within At-Risk
# ══════════════════════════════════════════════════════════════════
section_header("At-Risk theo RFM Segment & Priority")

if "rfm_segment" in filtered_wb.columns:
    seg_priority = (
        filtered_wb.groupby(["rfm_segment", "intervention_priority"], as_index=False)
        .agg(count=("Customer ID", "nunique"))
    )

    fig = px.bar(
        seg_priority,
        x="rfm_segment", y="count",
        color="intervention_priority",
        color_discrete_map=PRIORITY_COLORS,
        title="Phân bố Priority theo RFM Segment",
        barmode="stack",
    )
    fig.update_layout(
        height=420, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

insight_box(
    "Biểu đồ cho thấy nhóm <strong>Lost</strong> và <strong>Hibernating</strong> "
    "chiếm phần lớn P1 (Urgent). Đây là nhóm cần ưu tiên nguồn lực marketing cao nhất. "
    "Ngược lại, nhóm <strong>At Risk</strong> trong RFM chủ yếu ở mức P2/P3 — "
    "có cơ hội win-back cao hơn nếu can thiệp đúng thời điểm.",
    ref="InMobi (2023): Personalized win-back campaigns có tỷ lệ open rate 12–15% "
    "và conversion rate 2–5%, cao hơn 3x so với generic campaigns."
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  ROI Estimation
# ══════════════════════════════════════════════════════════════════
section_header("Ước tính ROI chiến dịch Win-back")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Tham số giả định")

    recovery_rate_p1 = st.slider("Recovery Rate P1 (%)", 5, 40, 15, key="rr_p1") / 100
    recovery_rate_p2 = st.slider("Recovery Rate P2 (%)", 10, 60, 30, key="rr_p2") / 100
    recovery_rate_p3 = st.slider("Recovery Rate P3 (%)", 30, 80, 55, key="rr_p3") / 100
    avg_ltv_recovered = st.slider("LTV trung bình recovered (£)", 50, 500, 150, key="ltv_rec")
    cost_per_campaign = st.slider("Chi phí mỗi campaign (£/KH)", 1, 20, 5, key="cpc")

with col2:
    st.markdown("#### Kết quả ước tính")

    recovered_p1 = int(p1_count * recovery_rate_p1)
    recovered_p2 = int(p2_count * recovery_rate_p2)
    recovered_p3 = int(p3_count * recovery_rate_p3)
    total_recovered = recovered_p1 + recovered_p2 + recovered_p3

    revenue_recovered = total_recovered * avg_ltv_recovered
    total_cost = total_at_risk * cost_per_campaign
    net_roi = revenue_recovered - total_cost

    metric_row([
        {"label": "KH recovered (est.)", "value": f"{total_recovered:,}"},
        {"label": "Revenue recovered", "value": f"£{revenue_recovered:,.0f}"},
    ])
    metric_row([
        {"label": "Chi phí campaign", "value": f"£{total_cost:,.0f}"},
        {"label": "Net ROI", "value": f"£{net_roi:,.0f}",
         "delta": f"{(net_roi/total_cost*100) if total_cost > 0 else 0:.0f}% return",
         "delta_color": "normal"},
    ])

if net_roi > 0:
    success_box(
        f"Với tỷ lệ recovery ước tính, chiến dịch win-back mang lại "
        f"<strong>£{net_roi:,.0f}</strong> doanh thu ròng (ROI "
        f"<strong>{(net_roi/total_cost*100) if total_cost > 0 else 0:.0f}%</strong>). "
        f"Tổng cộng <strong>{total_recovered:,}</strong> khách hàng có thể quay lại."
    )

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Win-back Playbook Table
# ══════════════════════════════════════════════════════════════════
section_header("Bảng hành động Win-back (Top 50)")

display_cols = [
    "Customer ID", "intervention_priority", "churn_probability",
    "rfm_segment", "at_risk_rule_bucket", "recency_vs_expected_gap",
    "customer_value_score", "last_product", "winback_action",
]
available = [c for c in display_cols if c in filtered_wb.columns]
st.dataframe(
    filtered_wb[available].head(50),
    use_container_width=True,
    height=500,
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Research References
# ══════════════════════════════════════════════════════════════════
section_header("Tài liệu tham khảo & Nghiên cứu")

st.markdown(
    """
    | # | Nguồn | Insight chính | Áp dụng |
    |---|-------|---------------|---------|
    | 1 | **Bain & Company** (Reichheld, 2001) | Tăng 5% retention → 25–95% profit | Justify ROI cho win-back |
    | 2 | **Harvard Business Review** | Acquire cost = 5–25× retain cost | Ưu tiên retention over acquisition |
    | 3 | **Retention Science** (2022) | Win-back success rate: 10–40% tùy timing | Benchmark cho recovery rate |
    | 4 | **McKinsey Digital** | ML prediction giảm 15–20% churn | Validate Random Forest approach |
    | 5 | **Kumar & Reinartz** (2016) | RFM + CLV là nền tảng CRM | Framework phân loại ưu tiên |
    | 6 | **Gupta & Lehmann** (2005) | Purchase cycle monitoring = best early detection | Cycle-based features |
    | 7 | **InMobi** (2023) | Personalized campaigns: 3× conversion vs generic | Cá nhân hóa chiến dịch |
    | 8 | **Statista** (2023) | E-commerce annual churn: 70–80% | Benchmark cho churn rate |
    """
)
