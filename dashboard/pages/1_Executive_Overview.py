"""Page 1 – Executive Overview.

Cung cấp cái nhìn tổng quan cho ban lãnh đạo:
KPIs, Retention Rate, phân bố khách hàng, hiệu quả kinh doanh.
"""
import sys
from pathlib import Path
_ROOT = str(Path(__file__).resolve().parents[2])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from dashboard.utils.data_loader import load_customer_360, load_time_series, load_model_metrics
from dashboard.components.metrics import (
    metric_row, inject_custom_css, inject_sidebar_brand, insight_box, section_header,
)
from dashboard.components.charts import pie_chart
from dashboard.components.filters import time_window_filter, resolve_window_metrics
from dashboard.utils.config import SEGMENT_COLORS, CHART_COLORS, BUSINESS_MODEL_COLORS

st.set_page_config(page_title="Executive Overview", page_icon="📊", layout="wide")
inject_custom_css()
inject_sidebar_brand()

# ── Header ───────────────────────────────────────────────────────
st.markdown("# Executive Overview")
st.caption("Tổng quan hiệu quả kinh doanh và sức khỏe tập khách hàng — Online Retail Dataset")

st.markdown(
    "Mọi chiến lược đúng đắn đều bắt đầu bằng việc nhìn thẳng vào số liệu — doanh thu đang vận động thế nào, "
    "bao nhiêu khách hàng đang có dấu hiệu rời bỏ, và tỷ lệ giữ chân nói lên điều gì. "
    "Reichheld — Bain & Company chỉ ra rằng chỉ cần cải thiện 5% retention, lợi nhuận có thể tăng 25 đến 95%. "
    "Con số này nghe lạ nhưng có lý do rất cụ thể: khách hàng cũ chi tiêu nhiều hơn, rẻ hơn để phục vụ, và dễ dự đoán hơn. "
    "Trang tổng quan này đưa ra bức tranh toàn cảnh trước khi chúng ta đi sâu vào từng nhóm khách hàng."
)

# ── Data ─────────────────────────────────────────────────────────
df = load_customer_360()
ts = load_time_series()
metrics = load_model_metrics()

# ── Sidebar: Time window ────────────────────────────────────────
with st.sidebar:
    st.subheader("Bộ lọc")
    window_days = time_window_filter(key="eo_tw")

df = resolve_window_metrics(df, window_days)
_window_label = f"{window_days}d"

# ══════════════════════════════════════════════════════════════════
#  KPIs
# ══════════════════════════════════════════════════════════════════
section_header("Chỉ số KPIs tổng quan")

total_customers = int((df["w_monetary"] > 0).sum())
total_revenue = float(df["w_monetary"].sum())
total_orders = int(df["w_frequency"].sum())
avg_ltv = float(df["customer_value_score"].mean())
churn_rate = float(df["churn_predicted"].mean())
retention_rate = 1 - churn_rate
avg_aov = total_revenue / total_orders if total_orders > 0 else 0

if window_days != 90:
    st.info(f"Hiển thị số liệu cho khoảng **{window_days} ngày** — {'dữ liệu chính xác' if window_days == 30 else 'ước tính từ dữ liệu 90 ngày'}")

metric_row([
    {"label": "Tổng khách hàng", "value": f"{total_customers:,}"},
    {"label": f"Tổng đơn hàng ({_window_label})", "value": f"{total_orders:,}"},
    {"label": f"Doanh thu ({_window_label})", "value": f"£{total_revenue:,.0f}"},
    {"label": "AOV", "value": f"£{avg_aov:,.2f}"},
    {"label": "Retention Rate", "value": f"{retention_rate:.1%}",
     "delta": f"-{churn_rate:.1%} churn", "delta_color": "inverse"},
])

insight_box(
    f"Trong <strong>{window_days} ngày</strong> gần nhất, doanh nghiệp phục vụ <strong>{total_customers:,}</strong> "
    f"khách hàng với doanh thu <strong>£{total_revenue:,.0f}</strong>. "
    f"Tỷ lệ giữ chân đạt <strong>{retention_rate:.1%}</strong>, "
    f"tương đương <strong>{churn_rate:.1%}</strong> khách hàng có nguy cơ rời bỏ.",
    ref="<a href='https://hbr.org/2014/10/the-value-of-keeping-the-right-customers' target='_blank'>Reichheld (2001) — Bain & Company / HBR</a>: Tăng 5% retention → +25–95% lợi nhuận. Chi phí giữ chân thấp hơn 5–25× so với tìm khách mới."
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Model Performance
# ══════════════════════════════════════════════════════════════════
section_header("Hiệu suất mô hình Churn Prediction")

metric_row([
    {"label": "Model", "value": metrics.get("model", "RF")},
    {"label": "Threshold", "value": f"{metrics['threshold']}"},
    {"label": "Recall", "value": f"{metrics['recall']:.2%}"},
    {"label": "Precision", "value": f"{metrics['precision']:.2%}"},
    {"label": "F1 Score", "value": f"{metrics['f1']:.4f}"},
    {"label": "ROC-AUC", "value": f"{metrics['roc_auc']:.4f}"},
])

insight_box(
    f"Mô hình Random Forest đạt <strong>Recall {metrics['recall']:.2%}</strong>, "
    f"nghĩa là nhận diện được phần lớn khách hàng có nguy cơ rời bỏ. "
    f"Việc ưu tiên Recall thay vì Precision là chiến lược phù hợp vì chi phí bỏ sót "
    f"một khách hàng at-risk (false negative) cao hơn nhiều so với chi phí chăm sóc "
    f"nhầm một khách hàng ổn định (false positive).",
    ref="<a href='https://hbr.org/2014/10/the-value-of-keeping-the-right-customers' target='_blank'>Harvard Business Review</a>: Chi phí thu hút khách hàng mới cao gấp 5–25 lần so với giữ chân khách hàng hiện tại."
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Revenue Trend & Customer Distribution
# ══════════════════════════════════════════════════════════════════
section_header("Tổng quan hiệu quả kinh doanh")

col1, col2 = st.columns([3, 2])

with col1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ts["month"], y=ts["revenue"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.08)",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(size=5),
        name="Revenue",
    ))
    fig.update_layout(
        title="Doanh thu theo tháng",
        xaxis_title="", yaxis_title="Revenue (£)",
        height=400,
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    seg_counts = (
        df.groupby("rfm_segment", as_index=False)
        .agg(count=("Customer ID", "nunique"))
        .sort_values("count", ascending=False)
    )
    fig = pie_chart(
        seg_counts, values="count", names="rfm_segment",
        title="Phân bố phân khúc RFM", color_map=SEGMENT_COLORS,
    )
    st.plotly_chart(fig, use_container_width=True)

# ── B2B / B2C Split ──────────────────────────────────────────────
if "customer_model" in df.columns:
    section_header("Phân bố B2B / B2C")
    col_b1, col_b2 = st.columns([2, 3])
    with col_b1:
        bm_counts = (
            df.groupby("customer_model", as_index=False)
            .agg(count=("Customer ID", "nunique"))
        )
        fig = pie_chart(
            bm_counts, values="count", names="customer_model",
            title="Tỷ lệ B2B vs B2C", color_map=BUSINESS_MODEL_COLORS,
        )
        st.plotly_chart(fig, use_container_width=True)
    with col_b2:
        bm_summary = (
            df.groupby("customer_model", as_index=False)
            .agg(
                customers=("Customer ID", "nunique"),
                avg_revenue=("monetary_90d", "mean"),
                avg_frequency=("frequency_90d", "mean"),
                avg_recency=("recency_days", "mean"),
                churn_rate=("churn_predicted", "mean"),
            )
        )
        bm_summary.columns = ["Loại KH", "Số KH", "Revenue TB (£)", "Freq TB", "Recency TB", "Churn Rate"]
        st.dataframe(
            bm_summary.style.format({
                "Revenue TB (£)": "{:,.0f}",
                "Freq TB": "{:.1f}",
                "Recency TB": "{:.0f}",
                "Churn Rate": "{:.1%}",
            }),
            use_container_width=True,
        )
    insight_box(
        f"Hệ thống phân loại <strong>{int(bm_counts.loc[bm_counts['customer_model']=='B2B / Account-like', 'count'].sum())}</strong> "
        f"khách B2B và <strong>{int(bm_counts.loc[bm_counts['customer_model']=='B2C / Consumer-like', 'count'].sum())}</strong> "
        f"khách B2C. Hai nhóm này có hành vi mua sắm rất khác nhau — "
        f"B2B mua số lượng lớn, tần suất cao; B2C mua lẻ, giá trị thấp hơn.",
        ref="<a href='https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-value-of-getting-personalization-right' target='_blank'>McKinsey Digital</a>: Tách biệt B2B và B2C trong phân tích CRM giúp tăng 15–25% hiệu quả chiến dịch retention."
    )
    st.divider()

rev_max_month = ts.loc[ts["revenue"].idxmax(), "month"]
rev_min_month = ts.loc[ts["revenue"].idxmin(), "month"]
insight_box(
    f"Doanh thu đạt đỉnh vào <strong>{rev_max_month.strftime('%m/%Y')}</strong> "
    f"và thấp nhất vào <strong>{rev_min_month.strftime('%m/%Y')}</strong>. "
    f"Xu hướng sụt giảm cuối kỳ có thể phản ánh hiệu ứng mùa vụ (seasonality) "
    f"hoặc dấu hiệu churn gia tăng.",
    ref="<a href='https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-value-of-getting-personalization-right' target='_blank'>McKinsey (2022)</a>: Phân tích xu hướng doanh thu kết hợp churn prediction giúp can thiệp sớm 2–3 tháng trước khi mất khách hàng."
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Monthly Active Customers & Orders
# ══════════════════════════════════════════════════════════════════
section_header("Khách hàng hoạt động & Đơn hàng theo tháng")

col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ts["month"], y=ts["customers"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(34,197,94,0.08)",
        line=dict(color="#22c55e", width=2.5),
        marker=dict(size=5),
        name="Active Customers",
    ))
    fig.update_layout(
        title="Monthly Active Customers",
        height=350, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ts["month"], y=ts["orders"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(139,92,246,0.08)",
        line=dict(color="#8b5cf6", width=2.5),
        marker=dict(size=5),
        name="Orders",
    ))
    fig.update_layout(
        title="Monthly Orders",
        height=350, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
#  Research References
# ══════════════════════════════════════════════════════════════════
section_header("Bối cảnh & Nghiên cứu tham khảo")

st.markdown(
    """
    | # | Nguồn | Insight chính | Áp dụng trong trang này |
    |---|-------|---------------|--------------------------|
    | 1 | [Reichheld (2001) — Bain & Company / HBR](https://hbr.org/2014/10/the-value-of-keeping-the-right-customers) | Tăng 5% retention → +25–95% lợi nhuận | Justify tầm quan trọng của Retention Rate KPI |
    | 2 | [Harvard Business Review](https://hbr.org/2014/10/the-value-of-keeping-the-right-customers) | Chi phí acquire khách mới = 5–25× chi phí retain | Lý do ưu tiên Recall trong mô hình churn |
    | 3 | [Kumar & Reinartz (2016) — JAMS / Springer](https://link.springer.com/article/10.1007/s11747-016-0488-7) | RFM + CLV là framework CRM cốt lõi | Nền tảng cho segmentation và scoring |
    | 4 | [Sun et al. (2023) — Heliyon / PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10570772/) | RFM + ML outperforms đơn lẻ cho noncontractual churn | Pipeline Random Forest + RFM features |
    | 5 | [McKinsey Digital (2022)](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-value-of-getting-personalization-right) | ML-based churn prediction giảm 15–20% tỷ lệ rời bỏ | Validate model approach |
    | 6 | [Statista (2023)](https://www.statista.com/statistics/816735/customer-churn-rate-by-industry-us/) | Tỷ lệ churn TMĐT trung bình: 70–80%/năm | Benchmark cho churn rate tổng quan |
    """
)
