"""Page 7 – B2B / B2C Segmentation.

Phân tích chi tiết hai nhóm khách hàng B2B (Account-like) và B2C (Consumer-like):
phân bố, so sánh metrics, behavior segments, và khuyến nghị chiến lược.
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

from dashboard.utils.data_loader import load_customer_360
from dashboard.components.metrics import (
    metric_row, inject_custom_css, inject_sidebar_brand, insight_box, section_header,
)
from dashboard.components.charts import pie_chart
from dashboard.components.filters import time_window_filter, resolve_window_metrics
from dashboard.utils.config import (
    BUSINESS_MODEL_COLORS, BEHAVIOR_SEGMENT_COLORS, CHART_COLORS,
)

st.set_page_config(page_title="B2B / B2C Segmentation", page_icon="📊", layout="wide")
inject_custom_css()
inject_sidebar_brand()

st.markdown("# B2B / B2C Customer Segmentation")
st.caption("Phân tích chi tiết hai nhóm khách hàng: B2B (Account-like) và B2C (Consumer-like)")

st.markdown(
    "Một sai lầm phổ biến trong phân tích CRM là xử lý tất cả khách hàng như một nhóm đồng nhất. "
    "Thực tế, khách doanh nghiệp (B2B) và khách cá nhân (B2C) có tư duy mua hàng, ngân sách, "
    "và lý do rời bỏ hoàn toàn khác nhau. "
    "Nghiên cứu của Tamaddoni và đồng nghiệp chỉ ra rằng B2B rời bỏ chủ yếu vì trải nghiệm dịch vụ kém — "
    "không phải sản phẩm; trong khi B2C bỏ đi khi cảm thấy không được cá nhân hóa. "
    "Hiểu rõ điều này trước khi thiết kế chiến dịch là cách tránh lãng phí ngân sách vào đúng người sai thông điệp."
)

# ── Data ─────────────────────────────────────────────────────────
df = load_customer_360()

# ── Sidebar: Time window ────────────────────────────────────────
with st.sidebar:
    st.subheader("Bộ lọc")
    window_days = time_window_filter(key="seg_tw")

df = resolve_window_metrics(df, window_days)
_window_label = f"{window_days}d"

if "customer_model" not in df.columns:
    st.warning(
        "Dữ liệu chưa có cột `customer_model`. "
        "Vui lòng chạy lại pipeline: `python -m src.dashboard.data_pipeline`"
    )
    st.stop()

# ══════════════════════════════════════════════════════════════════
#  Overview KPIs
# ══════════════════════════════════════════════════════════════════
section_header("Tổng quan B2B vs B2C")

b2b = df[df["customer_model"] == "B2B / Account-like"]
b2c = df[df["customer_model"] == "B2C / Consumer-like"]

metric_row([
    {"label": "Tổng khách hàng", "value": f"{len(df):,}"},
    {"label": "B2B (Account-like)", "value": f"{len(b2b):,}",
     "delta": f"{len(b2b)/len(df):.1%}"},
    {"label": "B2C (Consumer-like)", "value": f"{len(b2c):,}",
     "delta": f"{len(b2c)/len(df):.1%}"},
])

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Distribution Pie + Metrics Comparison
# ══════════════════════════════════════════════════════════════════
section_header("Phân bố & So sánh Metrics")

col1, col2 = st.columns([2, 3])

with col1:
    bm_counts = (
        df.groupby("customer_model", as_index=False)
        .agg(count=("Customer ID", "nunique"))
    )
    fig = pie_chart(
        bm_counts, values="count", names="customer_model",
        title="Tỷ lệ B2B vs B2C", color_map=BUSINESS_MODEL_COLORS,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    comparison = (
        df.groupby("customer_model", as_index=False)
        .agg(
            customers=("Customer ID", "nunique"),
            avg_monetary=("w_monetary", "mean"),
            median_monetary=("w_monetary", "median"),
            avg_frequency=("w_frequency", "mean"),
            avg_aov=("w_aov", "mean"),
            avg_recency=("recency_days", "mean"),
            avg_tenure=("tenure_days", "mean"),
            churn_rate=("churn_predicted", "mean"),
            avg_churn_risk=("churn_risk_index", "mean"),
        )
    )
    comparison.columns = [
        "Loại KH", "Số KH", f"Revenue TB ({_window_label}) (£)", f"Revenue Median ({_window_label}) (£)",
        f"Freq TB ({_window_label})", f"AOV TB ({_window_label}) (£)", "Recency TB", "Tenure TB",
        "Churn Rate", "Churn Risk Index",
    ]
    if window_days != 90:
        st.info(f"Bảng so sánh hiển thị số liệu {_window_label} — {'chính xác' if window_days == 30 else 'ước tính'}.")
    st.dataframe(
        comparison.style.format({
            f"Revenue TB ({_window_label}) (£)": "{:,.0f}",
            f"Revenue Median ({_window_label}) (£)": "{:,.0f}",
            f"Freq TB ({_window_label})": "{:.1f}",
            f"AOV TB ({_window_label}) (£)": "{:,.2f}",
            "Recency TB": "{:.0f}",
            "Tenure TB": "{:.0f}",
            "Churn Rate": "{:.1%}",
            "Churn Risk Index": "{:.3f}",
        }),
        use_container_width=True,
    )

insight_box(
    "B2B chiếm tỷ lệ nhỏ nhưng đóng góp doanh thu/khách cao hơn nhiều. "
    "B2C là nhóm lớn, mua lẻ với giá trị thấp hơn nhưng cần chiến lược khác biệt.",
    ref="Harvard Business Review: Chiến lược B2B retention tập trung vào account management, "
    "trong khi B2C cần loyalty programs và personalized offers."
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Box Plot Comparisons
# ══════════════════════════════════════════════════════════════════
section_header(f"Phân bố Monetary & Frequency ({_window_label}) theo nhóm")

col1, col2 = st.columns(2)

with col1:
    capped = df[df["w_monetary"] <= df["w_monetary"].quantile(0.95)]
    fig = px.box(
        capped, x="customer_model", y="w_monetary",
        color="customer_model",
        color_discrete_map=BUSINESS_MODEL_COLORS,
        title=f"Phân bố Monetary ({_window_label}) — capped 95th percentile",
    )
    fig.update_layout(
        height=400, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    capped_freq = df[df["w_frequency"] <= df["w_frequency"].quantile(0.95)]
    fig = px.box(
        capped_freq, x="customer_model", y="w_frequency",
        color="customer_model",
        color_discrete_map=BUSINESS_MODEL_COLORS,
        title=f"Phân bố Frequency ({_window_label}) — capped 95th percentile",
    )
    fig.update_layout(
        height=400, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Behavior Segments within each group
# ══════════════════════════════════════════════════════════════════
if "behavior_segment" in df.columns:
    section_header("Behavior Segments trong mỗi nhóm")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### B2B Segments")
        b2b_segs = (
            b2b.groupby("behavior_segment", as_index=False)
            .agg(
                count=("Customer ID", "nunique"),
                avg_monetary=("monetary_90d", "mean"),
                churn_rate=("churn_predicted", "mean"),
            )
            .sort_values("count", ascending=False)
        )
        fig = px.bar(
            b2b_segs, x="behavior_segment", y="count",
            color="behavior_segment",
            color_discrete_map=BEHAVIOR_SEGMENT_COLORS,
            title="Phân bố Segment — B2B",
            text="count",
        )
        fig.update_layout(
            height=380, template="plotly_white",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False, xaxis_title="", yaxis_title="Số KH",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            b2b_segs.rename(columns={
                "behavior_segment": "Segment", "count": "Số KH",
                "avg_monetary": "Revenue TB (£)", "churn_rate": "Churn Rate",
            }).style.format({
                "Revenue TB (£)": "{:,.0f}",
                "Churn Rate": "{:.1%}",
            }),
            use_container_width=True,
        )

    with col2:
        st.markdown("#### B2C Segments")
        b2c_segs = (
            b2c.groupby("behavior_segment", as_index=False)
            .agg(
                count=("Customer ID", "nunique"),
                avg_monetary=("monetary_90d", "mean"),
                churn_rate=("churn_predicted", "mean"),
            )
            .sort_values("count", ascending=False)
        )
        fig = px.bar(
            b2c_segs, x="behavior_segment", y="count",
            color="behavior_segment",
            color_discrete_map=BEHAVIOR_SEGMENT_COLORS,
            title="Phân bố Segment — B2C",
            text="count",
        )
        fig.update_layout(
            height=380, template="plotly_white",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False, xaxis_title="", yaxis_title="Số KH",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            b2c_segs.rename(columns={
                "behavior_segment": "Segment", "count": "Số KH",
                "avg_monetary": "Revenue TB (£)", "churn_rate": "Churn Rate",
            }).style.format({
                "Revenue TB (£)": "{:,.0f}",
                "Churn Rate": "{:.1%}",
            }),
            use_container_width=True,
        )

    insight_box(
        "B2B chủ yếu gồm <strong>Key Account / Strategic</strong> (giá trị cao, volume lớn) "
        "và <strong>Bulk / Wholesale</strong>. B2C phân bố đa dạng hơn: từ <strong>VIP / Loyal</strong> "
        "đến <strong>One-time / Occasional</strong>.",
    )

    st.divider()

# ══════════════════════════════════════════════════════════════════
#  Churn Risk by Business Model × Behavior Segment
# ══════════════════════════════════════════════════════════════════
if "behavior_segment" in df.columns:
    section_header("Churn Risk theo Business Model × Behavior Segment")

    heatmap_data = (
        df.groupby(["customer_model", "behavior_segment"], as_index=False)
        .agg(
            avg_churn_prob=("churn_probability", "mean"),
            count=("Customer ID", "nunique"),
        )
    )
    pivot = heatmap_data.pivot(
        index="behavior_segment", columns="customer_model", values="avg_churn_prob"
    ).fillna(0)

    fig = px.imshow(
        pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        color_continuous_scale="OrRd",
        title="Churn Probability TB theo Segment × Business Model",
        labels=dict(color="Churn Prob"),
        text_auto=".1%",
        aspect="auto",
    )
    fig.update_layout(
        height=450, template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Strategic Recommendations
# ══════════════════════════════════════════════════════════════════
section_header("Khuyến nghị chiến lược")

st.markdown("""
| Nhóm | Chiến lược ưu tiên | Hành động cụ thể |
|------|-------------------|------------------|
| **B2B — Key Account** | Account Management | Dedicated account manager, volume discount, SLA riêng |
| **B2B — Bulk/Wholesale** | Volume Retention | Chương trình giá theo tier, auto-replenishment reminders |
| **B2B — At Risk Account** | Urgent Win-back | Outreach trực tiếp, review pricing, flexible payment terms |
| **B2C — VIP/Loyal** | Loyalty Programs | Early access, exclusive offers, personalized recommendations |
| **B2C — Core Active** | Engagement | Cross-sell, newsletter, seasonal campaigns |
| **B2C — Explorer** | Cross-sell | Product bundles, "người khác cũng mua" suggestions |
| **B2C — One-time** | Activation | Welcome series, first-repeat incentive, onboarding email |
| **B2C — At Risk/Churned** | Win-back | Voucher mạnh, nhắc chu kỳ mua, survey lý do rời bỏ |
""")

insight_box(
    "Việc tách B2B và B2C giúp tránh nhầm lẫn chiến lược: "
    "không gửi voucher nhỏ cho khách B2B mua hàng triệu £, "
    "không áp dụng account management cho khách mua lẻ 1 lần.",
    ref="Gartner (2023): Personalization theo business model tăng 20-30% conversion rate "
    "so với chiến lược one-size-fits-all."
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
    | 1 | [Tamaddoni et al. (2014)](https://www.sciencedirect.com/science/article/abs/pii/S0019850113001600) — *Industrial Marketing Management* | Data-driven B2B churn prediction outperforms heuristics; B2B cần account-level features | Signal-based B2B classification (4 signals) |
    | 2 | [Rivo Industry Report (2026)](https://rivo.io/resources/customer-retention-statistics) | B2B retention: 82–90%; B2C: 74%. B2B churn do poor service (50%), không phải sản phẩm | Chiến lược khác nhau cho từng nhóm |
    | 3 | [Gartner (2023)](https://www.gartner.com/en/marketing/insights/articles/personalization-in-marketing) | Personalization theo business model tăng 20–30% conversion | Behavior segment riêng cho B2B vs B2C |
    | 4 | [Kumar & Reinartz (2016)](https://link.springer.com/article/10.1007/s11747-016-0488-7) — *JAMS* | B2B CLV phụ thuộc vào account expansion, B2C phụ thuộc vào repeat frequency | Revenue-at-risk calculation khác nhau |
    | 5 | [McKinsey Digital (2022)](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-value-of-getting-personalization-right) | Tách biệt B2B/B2C trong CRM analytics tăng 15–25% hiệu quả retention campaign | Filter B2B/B2C xuyên suốt dashboard |
    | 6 | [Rivo (2026) — B2B Loyalty](https://rivo.io/resources/b2b-loyalty-statistics) | B2B loyalty programs tăng retention 82%, tăng referrals 80%, ROI 4.8× | Key Account / Strategic segment cần loyalty riêng |
    """
)
