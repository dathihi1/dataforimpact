"""Page 2 – Purchasing Behavior Analytics.

Phân tích xu hướng mua sắm, danh mục sản phẩm, AOV, và phân khúc RFM.
"""
import sys
from pathlib import Path
_ROOT = str(Path(__file__).resolve().parents[2])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard.utils.data_loader import (
    load_customer_360, load_time_series, load_product_stats,
)
from dashboard.components.metrics import (
    metric_row, inject_custom_css, insight_box, section_header,
)
from dashboard.components.charts import pie_chart
from dashboard.components.filters import segment_filter
from dashboard.utils.config import SEGMENT_COLORS, CHART_COLORS

st.set_page_config(page_title="Purchasing Behavior", page_icon="📊", layout="wide")
inject_custom_css()

st.markdown("# Purchasing Behavior Analytics")
st.caption("Xu hướng mua sắm, danh mục sản phẩm, và phân khúc khách hàng")

# ── Data ─────────────────────────────────────────────────────────
df = load_customer_360()
ts = load_time_series()
products = load_product_stats()

# ── Sidebar Filters ──────────────────────────────────────────────
with st.sidebar:
    st.subheader("Bộ lọc")
    filtered_df = segment_filter(df, key="pb_seg")

# ══════════════════════════════════════════════════════════════════
#  KPIs
# ══════════════════════════════════════════════════════════════════
section_header("Tổng quan hành vi mua sắm")

n_customers = int(filtered_df["Customer ID"].nunique())
avg_aov = float(filtered_df["avg_order_value_90d"].mean())
avg_freq = float(filtered_df["frequency_90d"].mean())
avg_recency = float(filtered_df["recency_days"].mean())
median_tenure = float(filtered_df["tenure_days"].median())

metric_row([
    {"label": "Khách hàng", "value": f"{n_customers:,}"},
    {"label": "AOV trung bình", "value": f"£{avg_aov:.2f}"},
    {"label": "Tần suất mua (90d)", "value": f"{avg_freq:.1f}"},
    {"label": "Recency TB", "value": f"{avg_recency:.0f} ngày"},
    {"label": "Tenure TB", "value": f"{median_tenure:.0f} ngày"},
])

insight_box(
    f"Khách hàng trung bình mua <strong>{avg_freq:.1f} lần</strong> trong 90 ngày "
    f"với AOV <strong>£{avg_aov:.2f}</strong>. Recency trung bình "
    f"<strong>{avg_recency:.0f} ngày</strong> cho thấy "
    + ("khoảng cách mua khá dài — cần theo dõi chặt chẽ nhóm này." if avg_recency > 60
       else "nhìn chung khách hàng vẫn hoạt động."),
    ref="RFM Analysis (Bult & Wansbeek, 1995): Recency là yếu tố dự báo mạnh nhất "
    "cho hành vi mua lại tương lai."
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Revenue & AOV Trend
# ══════════════════════════════════════════════════════════════════
section_header("Xu hướng doanh thu & AOV theo thời gian")

col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ts["month"], y=ts["revenue"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.08)",
        line=dict(color="#3b82f6", width=2.5),
        name="Revenue",
    ))
    fig.update_layout(
        title="Doanh thu theo tháng (£)",
        height=400, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ts["month"], y=ts["aov"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(249,115,22,0.08)",
        line=dict(color="#f97316", width=2.5),
        name="AOV",
    ))
    fig.update_layout(
        title="AOV trung bình theo tháng (£)",
        height=400, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Product Categories — Top 15
# ══════════════════════════════════════════════════════════════════
section_header("Top 15 sản phẩm theo doanh thu")

top15 = products.head(15).copy()
top15 = top15.sort_values("total_revenue", ascending=True)

fig = go.Figure()
fig.add_trace(go.Bar(
    y=top15["Description"],
    x=top15["total_revenue"],
    orientation="h",
    marker=dict(color="#3b82f6"),
    text=[f"£{v:,.0f}" for v in top15["total_revenue"]],
    textposition="outside",
))
fig.update_layout(
    height=550,
    template="plotly_white",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Doanh thu (£)",
    yaxis_title="",
    margin=dict(l=20),
    font=dict(color="#334155"),
)
st.plotly_chart(fig, use_container_width=True)

insight_box(
    f"Top 15 sản phẩm chiếm phần lớn doanh thu. Sản phẩm bán chạy nhất là "
    f"<strong>{products.iloc[0]['Description']}</strong> với doanh thu "
    f"<strong>£{products.iloc[0]['total_revenue']:,.0f}</strong>. "
    f"Đây có thể là sản phẩm anchor để cross-sell các sản phẩm liên quan.",
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  AOV Distribution & Recency Distribution
# ══════════════════════════════════════════════════════════════════
section_header("Phân bố AOV & Recency")

col1, col2 = st.columns(2)

with col1:
    capped = filtered_df.loc[
        filtered_df["avg_order_value_90d"] <= filtered_df["avg_order_value_90d"].quantile(0.95)
    ]
    fig = px.histogram(
        capped, x="avg_order_value_90d", nbins=40,
        title="Phân bố AOV (capped 95th percentile)",
        color_discrete_sequence=["#3b82f6"],
        marginal="box",
    )
    fig.update_layout(
        height=400, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(
        filtered_df, x="recency_days", nbins=40,
        title="Phân bố Recency (ngày)",
        color_discrete_sequence=["#f97316"],
        marginal="box",
    )
    fig.update_layout(
        height=400, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  RFM Segments — Treemap
# ══════════════════════════════════════════════════════════════════
section_header("Phân khúc RFM — Treemap")

seg_counts = (
    filtered_df.groupby("rfm_segment", as_index=False)
    .agg(
        count=("Customer ID", "nunique"),
        avg_revenue=("monetary_90d", "mean"),
    )
)

fig = px.treemap(
    seg_counts,
    path=["rfm_segment"],
    values="count",
    color="avg_revenue",
    color_continuous_scale="Blues",
    title="Phân khúc khách hàng — kích thước = số KH, màu = doanh thu TB",
)
fig.update_layout(
    height=450, template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#334155"),
)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    fig = pie_chart(
        seg_counts, values="count", names="rfm_segment",
        title="Tỷ lệ phân khúc", color_map=SEGMENT_COLORS,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    seg_detail = (
        filtered_df.groupby("rfm_segment", as_index=False)
        .agg(
            n_customers=("Customer ID", "nunique"),
            avg_recency=("recency_days", "mean"),
            avg_frequency=("frequency_90d", "mean"),
            avg_monetary=("monetary_90d", "mean"),
            avg_churn_prob=("churn_probability", "mean"),
        )
        .sort_values("avg_monetary", ascending=False)
    )
    seg_detail.columns = ["Segment", "KH", "Recency TB", "Freq TB", "Revenue TB", "Churn Prob TB"]
    st.dataframe(seg_detail, use_container_width=True)

insight_box(
    "Phân khúc RFM giúp phân loại khách hàng theo 3 chiều: <strong>Recency</strong> (mua gần đây?), "
    "<strong>Frequency</strong> (mua thường xuyên?), <strong>Monetary</strong> (chi tiêu bao nhiêu?). "
    "Nhóm <strong>Champions</strong> và <strong>Loyal</strong> cần được giữ chân bằng loyalty programs, "
    "trong khi nhóm <strong>Lost</strong> và <strong>Hibernating</strong> cần chiến dịch win-back.",
    ref="Peter Fader, \"Customer Centricity\" (Wharton): RFM là nền tảng cho mọi "
    "chiến lược CRM data-driven."
)
