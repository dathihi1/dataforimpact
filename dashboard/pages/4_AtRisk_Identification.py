"""Page 4 – At-Risk Customer Identification.

Nhận diện khách hàng có nguy cơ rời bỏ, chỉ báo cảnh báo sớm,
phân bố xác suất churn theo segment.
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
    metric_row, inject_custom_css, insight_box, warning_box,
    danger_box, section_header,
)
from dashboard.utils.config import SEGMENT_COLORS, CHART_COLORS

st.set_page_config(page_title="At-Risk Identification", page_icon="📊", layout="wide")
inject_custom_css()

st.markdown("# At-Risk Customer Identification")
st.caption("Nhận diện & phân loại khách hàng có nguy cơ rời bỏ bằng ML + Rule-based scoring")

# ── Data ─────────────────────────────────────────────────────────
df = load_customer_360()

# ══════════════════════════════════════════════════════════════════
#  At-Risk Overview KPIs
# ══════════════════════════════════════════════════════════════════
section_header("Tổng quan At-Risk")

total = len(df)
predicted_churn = int(df["churn_predicted"].sum())
churn_pct = predicted_churn / total if total > 0 else 0
safe_count = total - predicted_churn

at_risk_rule = int((df.get("at_risk_rule_bucket") == "At Risk").sum()) if "at_risk_rule_bucket" in df.columns else 0
watchlist = int((df.get("at_risk_rule_bucket") == "Watchlist").sum()) if "at_risk_rule_bucket" in df.columns else 0
low_risk = int((df.get("at_risk_rule_bucket") == "Low Risk").sum()) if "at_risk_rule_bucket" in df.columns else 0

metric_row([
    {"label": "Tổng khách hàng", "value": f"{total:,}"},
    {"label": "Churn Predicted (ML)", "value": f"{predicted_churn:,}",
     "delta": f"{churn_pct:.1%}", "delta_color": "inverse"},
    {"label": "Safe", "value": f"{safe_count:,}"},
    {"label": "Rule: At Risk", "value": f"{at_risk_rule:,}"},
    {"label": "Rule: Watchlist", "value": f"{watchlist:,}"},
    {"label": "Rule: Low Risk", "value": f"{low_risk:,}"},
])

if churn_pct > 0.5:
    danger_box(
        f"<strong>Cảnh báo nghiêm trọng:</strong> Tỷ lệ churn dự đoán lên đến "
        f"<strong>{churn_pct:.1%}</strong>. "
        f"Hơn một nửa khách hàng có nguy cơ rời bỏ — cần triển khai chiến dịch "
        f"win-back khẩn cấp cho nhóm P1."
    )
elif churn_pct > 0.3:
    warning_box(
        f"<strong>Lưu ý:</strong> Tỷ lệ churn dự đoán ở mức <strong>{churn_pct:.1%}</strong>. "
        f"Cần theo dõi nhóm Watchlist và At Risk chặt chẽ."
    )

insight_box(
    f"Mô hình ML nhận diện <strong>{predicted_churn:,}</strong> khách hàng at-risk "
    f"(Recall-optimized). Song song đó, hệ thống rule-based phát hiện "
    f"<strong>{at_risk_rule:,}</strong> khách At Risk và <strong>{watchlist:,}</strong> "
    f"khách Watchlist dựa trên 6 tiêu chí hành vi.",
    ref="Benchmark ngành TMĐT: Tỷ lệ churn trung bình 70–80%/năm (Statista, 2023). "
    "Kết hợp ML + Rule-based giúp tăng độ phủ nhận diện (ensemble approach)."
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Churn Probability Distribution
# ══════════════════════════════════════════════════════════════════
section_header("Phân bố xác suất Churn")

col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        df, x="churn_probability", nbins=50,
        color_discrete_sequence=["#ef4444"],
        title="Phân bố Churn Probability (toàn bộ KH)",
        marginal="violin",
    )
    fig.add_vline(x=0.5, line_dash="dash", line_color="#f59e0b",
                  annotation_text="Threshold 0.5", annotation_position="top right")
    fig.update_layout(
        height=420, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    if "at_risk_rule_bucket" in df.columns:
        bucket_counts = (
            df.groupby("at_risk_rule_bucket", as_index=False, observed=False)
            .agg(count=("Customer ID", "nunique"))
        )
        colors = ["#22c55e", "#f59e0b", "#ef4444"]
        fig = go.Figure(data=[go.Bar(
            x=bucket_counts["at_risk_rule_bucket"].astype(str),
            y=bucket_counts["count"],
            marker_color=colors[:len(bucket_counts)],
            text=bucket_counts["count"],
            textposition="auto",
        )])
        fig.update_layout(
            title="Phân bố At-Risk Rule Buckets",
            height=420, template="plotly_white",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="", yaxis_title="Số khách hàng",
            font=dict(color="#334155"),
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Segment-level Churn Breakdown
# ══════════════════════════════════════════════════════════════════
section_header("Churn theo phân khúc RFM")

seg_churn = (
    df.groupby("rfm_segment", as_index=False)
    .agg(
        total=("Customer ID", "nunique"),
        churn_count=("churn_predicted", "sum"),
        avg_churn_prob=("churn_probability", "mean"),
    )
)
seg_churn["churn_rate"] = seg_churn["churn_count"] / seg_churn["total"]
seg_churn = seg_churn.sort_values("churn_rate", ascending=True)

fig = go.Figure()
fig.add_trace(go.Bar(
    y=seg_churn["rfm_segment"],
    x=seg_churn["churn_rate"],
    orientation="h",
    marker=dict(
        color=seg_churn["churn_rate"],
        colorscale="OrRd",
        showscale=True,
        colorbar=dict(title="Churn Rate"),
    ),
    text=[f"{v:.1%}" for v in seg_churn["churn_rate"]],
    textposition="outside",
))
fig.update_layout(
    title="Tỷ lệ Churn theo RFM Segment",
    height=400, template="plotly_white",
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Churn Rate", yaxis_title="",
    xaxis=dict(tickformat=".0%"),
    font=dict(color="#334155"),
)
st.plotly_chart(fig, use_container_width=True)

seg_display = seg_churn.copy()
seg_display.columns = ["Segment", "Total KH", "Churn KH", "Churn Prob TB", "Churn Rate"]
st.dataframe(
    seg_display.sort_values("Churn Rate", ascending=False).style.format({
        "Churn Prob TB": "{:.2%}",
        "Churn Rate": "{:.2%}",
    }),
    use_container_width=True,
)

insight_box(
    "Phân tích cho thấy tỷ lệ churn <strong>không đồng đều</strong> giữa các segment. "
    "Nhóm <strong>Lost</strong> và <strong>Hibernating</strong> có tỷ lệ churn cao nhất — "
    "đây là nhóm ưu tiên cho chiến dịch win-back. Ngược lại, nhóm <strong>Champions</strong> "
    "có tỷ lệ churn thấp nhất — cần loyalty programs để duy trì.",
    ref="Pareto Principle trong CRM: 20% khách hàng tạo 80% doanh thu — "
    "ưu tiên giữ chân nhóm Champions/Loyal trước."
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Early Warning Indicators
# ══════════════════════════════════════════════════════════════════
section_header("Chỉ báo cảnh báo sớm (Early Warning)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Recency > 90 ngày")
    high_recency = (
        df[df["recency_days"] >= 90]
        .sort_values("churn_probability", ascending=False)
        .head(15)
    )
    display_cols = ["Customer ID", "recency_days", "rfm_segment",
                    "churn_probability", "customer_value_score"]
    available = [c for c in display_cols if c in high_recency.columns]
    st.dataframe(high_recency[available], use_container_width=True, height=350)
    st.caption(f"Tổng: {len(df[df['recency_days'] >= 90]):,} khách hàng")

with col2:
    st.markdown("#### Order Rate Ratio < 0.5")
    if "order_rate_ratio" in df.columns:
        low_freq = (
            df[df["order_rate_ratio"] < 0.5]
            .sort_values("churn_probability", ascending=False)
            .head(15)
        )
        display_cols = ["Customer ID", "order_rate_ratio", "rfm_segment",
                        "churn_probability", "customer_value_score"]
        available = [c for c in display_cols if c in low_freq.columns]
        st.dataframe(low_freq[available], use_container_width=True, height=350)
        st.caption(f"Tổng: {len(df[df['order_rate_ratio'] < 0.5]):,} khách hàng")

st.divider()

# ══════════════════════════════════════════════════════════════════
#  At-Risk Customer Table
# ══════════════════════════════════════════════════════════════════
section_header("Bảng chi tiết khách hàng At-Risk (Top 50)")

at_risk_df = (
    df[df["churn_predicted"] == 1]
    .sort_values("churn_probability", ascending=False)
    .head(50)
)

display_cols = [
    "Customer ID", "churn_probability", "rfm_segment",
    "at_risk_rule_bucket", "recency_days", "frequency_90d",
    "monetary_90d", "customer_value_score", "cycle_risk_score",
]
available = [c for c in display_cols if c in at_risk_df.columns]
st.dataframe(at_risk_df[available], use_container_width=True, height=450)
