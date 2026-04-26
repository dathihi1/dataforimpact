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
    metric_row, inject_custom_css, inject_sidebar_brand, insight_box, section_header,
)
from dashboard.components.charts import pie_chart
from dashboard.components.filters import segment_filter, business_model_filter, time_window_filter, resolve_window_metrics
from dashboard.utils.config import SEGMENT_COLORS, CHART_COLORS, BUSINESS_MODEL_COLORS

st.set_page_config(page_title="Purchasing Behavior", page_icon="📊", layout="wide")
inject_custom_css()
inject_sidebar_brand()

st.markdown("# Purchasing Behavior")
st.caption("Phân tích hành vi mua sắm: xu hướng doanh thu, AOV, sản phẩm bán chạy, phân khúc RFM")

st.markdown(
    "Phân tích hành vi mua sắm không chỉ là đếm đơn hàng — mà là hiểu nhịp điệu chi tiêu của khách hàng. "
    "Bult & Wansbeek đã chứng minh từ những năm 90 rằng Recency — tức là lần mua gần nhất — "
    "là dấu hiệu đáng tin cậy nhất để dự đoán ai sẽ quay lại. "
    "Khách mua tuần trước khác hoàn toàn với khách mua 3 tháng trước, dù doanh thu của họ giống nhau. "
    "Trang này đi vào chi tiết: doanh thu biến động theo thời gian ra sao, sản phẩm nào đang kéo tăng trưởng, "
    "và các phân khúc RFM đang phân bổ thế nào trong tổng thể khách hàng."
)

# ── Data ─────────────────────────────────────────────────────────
df = load_customer_360()
ts = load_time_series()
products = load_product_stats()

# ── Sidebar Filters ──────────────────────────────────────────────
with st.sidebar:
    st.subheader("Bộ lọc")
    window_days = time_window_filter(key="pb_tw")
    df = business_model_filter(df, key="pb_bm")
    filtered_df = segment_filter(df, key="pb_seg")

filtered_df = resolve_window_metrics(filtered_df, window_days)
_window_label = f"{window_days}d"

# ══════════════════════════════════════════════════════════════════
#  KPIs
# ══════════════════════════════════════════════════════════════════
section_header("Tổng quan hành vi mua sắm")

n_customers = int((filtered_df["w_monetary"] > 0).sum())
avg_aov = float(filtered_df["w_aov"].mean())
avg_freq = float(filtered_df["w_frequency"].mean())
avg_revenue = float(filtered_df["w_monetary"].sum())
avg_recency = float(filtered_df["recency_days"].mean())
median_tenure = float(filtered_df["tenure_days"].median())

if window_days != 90:
    st.info(f"Hiển thị số liệu cho khoảng **{window_days} ngày** — {'dữ liệu chính xác' if window_days == 30 else 'ước tính từ dữ liệu 90 ngày'}")

metric_row([
    {"label": "Khách hàng", "value": f"{n_customers:,}"},
    {"label": f"Doanh thu ({_window_label})", "value": f"£{avg_revenue:,.0f}"},
    {"label": f"AOV ({_window_label})", "value": f"£{avg_aov:.2f}"},
    {"label": f"Freq TB ({_window_label})", "value": f"{avg_freq:.1f}"},
    {"label": "Recency TB", "value": f"{avg_recency:.0f} ngày"},
    {"label": "Tenure TB", "value": f"{median_tenure:.0f} ngày"},
])

insight_box(
    f"Khách hàng trung bình mua <strong>{avg_freq:.1f} lần</strong> trong <strong>{window_days} ngày</strong> "
    f"với AOV <strong>£{avg_aov:.2f}</strong>. Recency trung bình "
    f"<strong>{avg_recency:.0f} ngày</strong> cho thấy "
    + ("khoảng cách mua khá dài — cần theo dõi chặt chẽ nhóm này." if avg_recency > 60
       else "nhìn chung khách hàng vẫn hoạt động."),
    ref="<a href='https://link.springer.com/article/10.1023/A:1008008402697' target='_blank'>Bult & Wansbeek (1995) — Marketing Science</a>: Recency là yếu tố dự báo mạnh nhất cho hành vi mua lại. Khách mua gần nhất có xác suất quay lại cao nhất."
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
    ref="<a href='https://marketing.wharton.upenn.edu/profile/faderp/' target='_blank'>Peter Fader — Wharton Business School</a>: RFM là nền tảng của mọi chiến lược CRM data-driven. "
    "Nhóm Champions và Loyal tạo phần lớn doanh thu — giữ chân nhóm này là ưu tiên số 1."
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  B2B vs B2C Behavior Comparison
# ══════════════════════════════════════════════════════════════════
if "customer_model" in filtered_df.columns:
    section_header("So sánh hành vi B2B vs B2C")

    bm_behavior = (
        filtered_df.groupby("customer_model", as_index=False)
        .agg(
            customers=("Customer ID", "nunique"),
            avg_aov=("avg_order_value_90d", "mean"),
            avg_frequency=("frequency_90d", "mean"),
            avg_monetary=("monetary_90d", "mean"),
            avg_recency=("recency_days", "mean"),
            churn_rate=("churn_predicted", "mean"),
        )
    )
    bm_behavior.columns = ["Loại KH", "Số KH", "AOV TB", "Freq TB", "Monetary TB", "Recency TB", "Churn Rate"]

    col1, col2 = st.columns(2)
    with col1:
        metrics_to_compare = ["AOV TB", "Monetary TB"]
        fig = go.Figure()
        for _, row in bm_behavior.iterrows():
            fig.add_trace(go.Bar(
                name=row["Loại KH"],
                x=metrics_to_compare,
                y=[row["AOV TB"], row["Monetary TB"]],
                marker_color=BUSINESS_MODEL_COLORS.get(row["Loại KH"], "#999"),
            ))
        fig.update_layout(
            title="So sánh AOV & Monetary (£)",
            barmode="group", height=380,
            template="plotly_white",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.dataframe(
            bm_behavior.style.format({
                "AOV TB": "£{:,.2f}",
                "Freq TB": "{:.1f}",
                "Monetary TB": "£{:,.0f}",
                "Recency TB": "{:.0f}",
                "Churn Rate": "{:.1%}",
            }),
            use_container_width=True,
        )

    insight_box(
        "B2B (Account-like) thường có <strong>AOV</strong> và <strong>Monetary</strong> cao hơn nhiều so với B2C, "
        "nhưng số lượng ít hơn. Chiến lược retention cần được tách riêng: B2B ưu tiên account management, "
        "B2C ưu tiên loyalty programs và cross-sell.",
        ref="<a href='https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-value-of-getting-personalization-right' target='_blank'>McKinsey Digital (2022)</a>: "
        "Tách biệt chiến lược B2B/B2C tăng 15–25% hiệu quả retention campaign. "
        "<a href='https://rivo.io/resources/customer-retention-statistics' target='_blank'>Rivo (2026)</a>: B2B retention 82–90%, B2C 74%.",
    )

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Research References
# ══════════════════════════════════════════════════════════════════
section_header("Tài liệu tham khảo & Nghiên cứu")

st.markdown(
    """
    | # | Nguồn | Insight chính | Áp dụng trong trang này |
    |---|-------|---------------|--------------------------|
    | 1 | [Bult & Wansbeek (1995) — Marketing Science](https://link.springer.com/article/10.1023/A:1008008402697) | Recency là predictor mạnh nhất cho hành vi mua lại trong direct marketing | KPI Recency TB và phân tích recency distribution |
    | 2 | [Peter Fader — Wharton (Customer Centricity)](https://marketing.wharton.upenn.edu/profile/faderp/) | RFM là nền tảng mọi chiến lược CRM — không phải mọi khách đều có giá trị như nhau | RFM Treemap, phân khúc Champions/Lost/Loyal |
    | 3 | [Lemon & Verhoef (2016) — Journal of Marketing](https://journals.sagepub.com/doi/10.1509/jm.15.0420) | Customer journey gồm pre-purchase → purchase → post-purchase ảnh hưởng đến loyalty | Revenue trend và hành vi mua theo thời gian |
    | 4 | [McKinsey Digital (2022)](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-value-of-getting-personalization-right) | Tách biệt B2B/B2C trong CRM analytics tăng 15–25% hiệu quả | So sánh AOV và Monetary B2B vs B2C |
    | 5 | [Rivo Industry Report (2026)](https://rivo.io/resources/customer-retention-statistics) | B2B retention: 82–90%; B2C: 74% — hai nhóm cần chiến lược riêng | Insight box B2B vs B2C comparison |
    | 6 | [Kumar & Reinartz (2016) — JAMS / Springer](https://link.springer.com/article/10.1007/s11747-016-0488-7) | Kết hợp RFM + CLV tối ưu hóa phân bổ ngân sách retention | Phân khúc RFM và customer value scoring |
    """
)
