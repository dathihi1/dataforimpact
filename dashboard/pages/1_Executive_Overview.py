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
    metric_row, inject_custom_css, insight_box, section_header,
)
from dashboard.components.charts import pie_chart
from dashboard.utils.config import SEGMENT_COLORS, CHART_COLORS

st.set_page_config(page_title="Executive Overview", page_icon="📊", layout="wide")
inject_custom_css()

# ── Header ───────────────────────────────────────────────────────
st.markdown("# Executive Overview")
st.caption("Tổng quan hiệu quả kinh doanh và sức khỏe tập khách hàng — Online Retail Dataset")

# ── Data ─────────────────────────────────────────────────────────
df = load_customer_360()
ts = load_time_series()
metrics = load_model_metrics()

# ══════════════════════════════════════════════════════════════════
#  KPIs
# ══════════════════════════════════════════════════════════════════
section_header("Chỉ số KPIs tổng quan")

total_customers = int(df["Customer ID"].nunique())
total_revenue = float(df["monetary_90d"].sum())
total_orders = int(df["frequency_90d"].sum())
avg_ltv = float(df["customer_value_score"].mean())
churn_rate = float(df["churn_predicted"].mean())
retention_rate = 1 - churn_rate
avg_aov = total_revenue / total_orders if total_orders > 0 else 0

metric_row([
    {"label": "Tổng khách hàng", "value": f"{total_customers:,}"},
    {"label": "Tổng đơn hàng (90d)", "value": f"{total_orders:,}"},
    {"label": "Doanh thu (90d)", "value": f"£{total_revenue:,.0f}"},
    {"label": "AOV", "value": f"£{avg_aov:,.2f}"},
    {"label": "Retention Rate", "value": f"{retention_rate:.1%}",
     "delta": f"-{churn_rate:.1%} churn", "delta_color": "inverse"},
])

insight_box(
    f"Trong 90 ngày gần nhất, doanh nghiệp phục vụ <strong>{total_customers:,}</strong> "
    f"khách hàng với doanh thu <strong>£{total_revenue:,.0f}</strong>. "
    f"Tỷ lệ giữ chân đạt <strong>{retention_rate:.1%}</strong>, "
    f"tương đương <strong>{churn_rate:.1%}</strong> khách hàng có nguy cơ rời bỏ.",
    ref="Theo Bain & Company, tăng 5% tỷ lệ giữ chân có thể tăng 25–95% lợi nhuận "
    "(Frederick Reichheld, \"Prescription for Cutting Costs\", Bain & Co.)."
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
    ref="Harvard Business Review: Chi phí thu hút khách hàng mới cao gấp 5–25 lần "
    "so với giữ chân khách hàng hiện tại."
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

rev_max_month = ts.loc[ts["revenue"].idxmax(), "month"]
rev_min_month = ts.loc[ts["revenue"].idxmin(), "month"]
insight_box(
    f"Doanh thu đạt đỉnh vào <strong>{rev_max_month.strftime('%m/%Y')}</strong> "
    f"và thấp nhất vào <strong>{rev_min_month.strftime('%m/%Y')}</strong>. "
    f"Xu hướng sụt giảm cuối kỳ có thể phản ánh hiệu ứng mùa vụ (seasonality) "
    f"hoặc dấu hiệu churn gia tăng.",
    ref="McKinsey: Phân tích xu hướng doanh thu kết hợp churn prediction giúp doanh nghiệp "
    "can thiệp sớm 2–3 tháng trước khi mất khách hàng."
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
    | Nguồn | Insight chính |
    |-------|---------------|
    | **Bain & Company** (Reichheld, 2001) | Tăng 5% retention → tăng 25–95% lợi nhuận |
    | **Harvard Business Review** | Chi phí acquire khách mới = 5–25× chi phí retain |
    | **McKinsey Digital** | ML-based churn prediction giảm 15–20% tỷ lệ rời bỏ |
    | **Gartner** (2023) | 80% doanh thu tương lai đến từ 20% khách hàng hiện tại |
    | **E-commerce benchmark** | Tỷ lệ churn trung bình ngành TMĐT: 70–80%/năm |
    """
)
