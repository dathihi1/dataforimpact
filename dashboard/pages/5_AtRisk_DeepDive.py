"""Page 5 – At-Risk Behavior Deep Dive.

Phân tích chi tiết hành vi nhóm at-risk: sụt giảm tần suất,
khoảng cách đơn hàng, giá trị giỏ hàng, và hành vi hủy/trả hàng.
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

from dashboard.utils.data_loader import load_customer_360
from dashboard.components.metrics import (
    metric_row, inject_custom_css, insight_box, warning_box,
    section_header,
)
from dashboard.utils.config import SEGMENT_COLORS, CHART_COLORS

st.set_page_config(page_title="At-Risk Deep Dive", page_icon="📊", layout="wide")
inject_custom_css()

st.markdown("# At-Risk Behavior Deep Dive")
st.caption("Mẫu hình hành vi đặc trưng của nhóm khách hàng có nguy cơ rời bỏ")

# ── Data ─────────────────────────────────────────────────────────
df = load_customer_360()
at_risk = df[df["churn_predicted"] == 1].copy()
safe = df[df["churn_predicted"] == 0].copy()

# ══════════════════════════════════════════════════════════════════
#  At-Risk vs Safe — Summary Comparison
# ══════════════════════════════════════════════════════════════════
section_header("So sánh At-Risk vs Safe")

def _safe_mean(series):
    return float(series.mean()) if len(series) > 0 else 0.0

comparison_metrics = {
    "Recency (ngày)": (_safe_mean(at_risk["recency_days"]), _safe_mean(safe["recency_days"])),
    "Frequency (90d)": (_safe_mean(at_risk["frequency_90d"]), _safe_mean(safe["frequency_90d"])),
    "AOV (£)": (_safe_mean(at_risk["avg_order_value_90d"]), _safe_mean(safe["avg_order_value_90d"])),
    "Monetary (£)": (_safe_mean(at_risk["monetary_90d"]), _safe_mean(safe["monetary_90d"])),
    "Churn Risk Index": (_safe_mean(at_risk["churn_risk_index"]), _safe_mean(safe["churn_risk_index"])),
    "Return Rate": (_safe_mean(at_risk["return_rate_90d"]), _safe_mean(safe["return_rate_90d"])),
}

comp_df = pd.DataFrame(comparison_metrics, index=["At-Risk", "Safe"]).T.reset_index()
comp_df.columns = ["Metric", "At-Risk", "Safe"]
comp_df["Difference"] = comp_df["At-Risk"] - comp_df["Safe"]
comp_df["Direction"] = comp_df["Difference"].apply(lambda x: "Cao hơn" if x > 0 else "Thấp hơn")

fig = go.Figure()
fig.add_trace(go.Bar(
    name="At-Risk", x=comp_df["Metric"], y=comp_df["At-Risk"],
    marker_color="#ef4444", text=[f"{v:.1f}" for v in comp_df["At-Risk"]],
    textposition="auto",
))
fig.add_trace(go.Bar(
    name="Safe", x=comp_df["Metric"], y=comp_df["Safe"],
    marker_color="#22c55e", text=[f"{v:.1f}" for v in comp_df["Safe"]],
    textposition="auto",
))
fig.update_layout(
    title="So sánh trung bình: At-Risk vs Safe",
    barmode="group", height=420,
    template="plotly_white",
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#334155"),
)
st.plotly_chart(fig, use_container_width=True)

st.dataframe(comp_df.style.format({
    "At-Risk": "{:.2f}", "Safe": "{:.2f}", "Difference": "{:+.2f}",
}), use_container_width=True)

insight_box(
    "Nhóm At-Risk có <strong>Recency cao hơn</strong> (mua từ lâu), "
    "<strong>Frequency thấp hơn</strong> (mua ít hơn), và "
    "<strong>Churn Risk Index cao hơn</strong> so với nhóm Safe. "
    "Đây là mẫu hình cổ điển của churn: khách hàng dần rời xa trước khi rời bỏ hoàn toàn.",
    ref="Kumar & Reinartz (2016): \"Customer Relationship Management\" — "
    "3 tín hiệu mạnh nhất cho churn: tăng recency, giảm frequency, giảm monetary."
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Frequency & Spend Momentum
# ══════════════════════════════════════════════════════════════════
section_header("Xu hướng sụt giảm (Momentum)")

col1, col2 = st.columns(2)

with col1:
    if "frequency_momentum" in at_risk.columns:
        fig = px.histogram(
            at_risk, x="frequency_momentum", nbins=30,
            color_discrete_sequence=["#ef4444"],
            title="Frequency Momentum (At-Risk)",
            marginal="box",
        )
        fig.add_vline(x=0, line_dash="dash", line_color="#94a3b8",
                      annotation_text="Baseline = 0")
        fig.update_layout(
            height=400, template="plotly_white",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155"),
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if "spend_momentum" in at_risk.columns:
        fig = px.histogram(
            at_risk, x="spend_momentum", nbins=30,
            color_discrete_sequence=["#f97316"],
            title="Spend Momentum (At-Risk)",
            marginal="box",
        )
        fig.add_vline(x=0, line_dash="dash", line_color="#94a3b8",
                      annotation_text="Baseline = 0")
        fig.update_layout(
            height=400, template="plotly_white",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155"),
        )
        st.plotly_chart(fig, use_container_width=True)

if "frequency_momentum" in at_risk.columns:
    neg_freq = (at_risk["frequency_momentum"] < 0).mean()
    neg_spend = (at_risk["spend_momentum"] < 0).mean() if "spend_momentum" in at_risk.columns else 0
    warning_box(
        f"<strong>{neg_freq:.1%}</strong> khách hàng at-risk có frequency momentum âm "
        f"(giảm tần suất mua), và <strong>{neg_spend:.1%}</strong> có spend momentum âm "
        f"(giảm chi tiêu). Momentum < 0 cho thấy xu hướng rời bỏ đang tăng tốc."
    )

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Inter-purchase Gap & Cycle Risk
# ══════════════════════════════════════════════════════════════════
section_header("Khoảng cách mua & Cycle Risk")

col1, col2 = st.columns(2)

with col1:
    if "recency_vs_expected_gap" in at_risk.columns:
        capped = at_risk.loc[
            at_risk["recency_vs_expected_gap"]
            <= at_risk["recency_vs_expected_gap"].quantile(0.95)
        ]
        fig = px.histogram(
            capped, x="recency_vs_expected_gap", nbins=40,
            color_discrete_sequence=["#8b5cf6"],
            title="Recency / Expected Gap (At-Risk)",
            marginal="box",
        )
        fig.add_vline(x=1.0, line_dash="dash", line_color="#22c55e",
                      annotation_text="Đúng chu kỳ (1.0)")
        fig.add_vline(x=1.5, line_dash="dash", line_color="#f59e0b",
                      annotation_text="Cycle break (1.5)")
        fig.update_layout(
            height=420, template="plotly_white",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155"),
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    if "cycle_risk_score" in at_risk.columns:
        at_risk_valid = at_risk.dropna(subset=["cycle_risk_score"])
        fig = px.histogram(
            at_risk_valid, x="cycle_risk_score", nbins=30,
            color_discrete_sequence=["#3b82f6"],
            title="Cycle Risk Score (At-Risk)",
            marginal="box",
        )
        fig.update_layout(
            height=420, template="plotly_white",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155"),
        )
        st.plotly_chart(fig, use_container_width=True)

insight_box(
    "Tỉ số <strong>Recency / Expected Gap > 1.5</strong> là ngưỡng \"cycle break\" — "
    "khách hàng đã vượt quá 50% thời gian mua kỳ vọng mà chưa quay lại. "
    "Đây là dấu hiệu mạnh nhất cho thấy khách hàng sắp rời bỏ.",
    ref="Gupta & Lehmann (2005): \"Managing Customers as Investments\" — "
    "Monitoring purchase cycles là phương pháp hiệu quả nhất cho early churn detection."
)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Order Rate vs Spend Rate (Scatter)
# ══════════════════════════════════════════════════════════════════
section_header("Order Rate vs Spend Rate (At-Risk)")

if "order_rate_ratio" in at_risk.columns and "spend_rate_ratio" in at_risk.columns:
    capped = at_risk.loc[
        (at_risk["order_rate_ratio"] <= at_risk["order_rate_ratio"].quantile(0.95))
        & (at_risk["spend_rate_ratio"] <= at_risk["spend_rate_ratio"].quantile(0.95))
    ]

    fig = px.scatter(
        capped,
        x="order_rate_ratio", y="spend_rate_ratio",
        color="rfm_segment" if "rfm_segment" in capped.columns else None,
        color_discrete_map=SEGMENT_COLORS,
        size="churn_probability",
        hover_data=["Customer ID"],
        title="Order Rate Ratio vs Spend Rate Ratio",
    )
    fig.add_hline(y=1.0, line_dash="dash", line_color="#cbd5e1")
    fig.add_vline(x=1.0, line_dash="dash", line_color="#cbd5e1")
    fig.add_annotation(x=0.3, y=0.3, text="High Risk Zone",
                       showarrow=False, font=dict(color="#ef4444", size=13))
    fig.update_layout(
        height=500, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Return Rate Comparison
# ══════════════════════════════════════════════════════════════════
section_header("Hành vi hủy/trả hàng")

col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        at_risk, x="return_rate_90d", nbins=30,
        color_discrete_sequence=["#ef4444"],
        title="Return Rate Distribution (At-Risk)",
    )
    fig.update_layout(
        height=350, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(
        safe, x="return_rate_90d", nbins=30,
        color_discrete_sequence=["#22c55e"],
        title="Return Rate Distribution (Safe)",
    )
    fig.update_layout(
        height=350, template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    st.plotly_chart(fig, use_container_width=True)

avg_return_risk = _safe_mean(at_risk["return_rate_90d"])
avg_return_safe = _safe_mean(safe["return_rate_90d"])
metric_row([
    {"label": "Return Rate TB (At-Risk)", "value": f"{avg_return_risk:.2%}"},
    {"label": "Return Rate TB (Safe)", "value": f"{avg_return_safe:.2%}"},
    {"label": "Chênh lệch", "value": f"{avg_return_risk - avg_return_safe:+.2%}",
     "delta_color": "inverse"},
])

insight_box(
    f"Tỷ lệ trả hàng của nhóm At-Risk (<strong>{avg_return_risk:.2%}</strong>) "
    f"{'cao hơn' if avg_return_risk > avg_return_safe else 'thấp hơn'} "
    f"nhóm Safe (<strong>{avg_return_safe:.2%}</strong>). "
    "Tỷ lệ trả hàng cao có thể phản ánh sự không hài lòng — "
    "một yếu tố góp phần vào quyết định rời bỏ.",
    ref="Petersen & Kumar (2009): Tỷ lệ return cao liên quan chặt với churn; "
    "cải thiện trải nghiệm sản phẩm giảm 15% churn rate."
)
