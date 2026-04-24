"""Page 3 – Product Recommendation.

Hồ sơ khách hàng, nhóm tương đồng (Lookalike), gợi ý sản phẩm mua kèm.
"""
import sys
from pathlib import Path
_ROOT = str(Path(__file__).resolve().parents[2])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard.utils.data_loader import load_customer_360, load_product_stats
from dashboard.components.metrics import (
    metric_row, inject_custom_css, insight_box, success_box,
    section_header,
)
from dashboard.utils.config import SEGMENT_COLORS

st.set_page_config(page_title="Product Recommendation", page_icon="📊", layout="wide")
inject_custom_css()

st.markdown("# Product Recommendation")
st.caption("Hồ sơ mua sắm cá nhân, nhóm khách hàng tương đồng, gợi ý cross-sell/up-sell")

# ── Data ─────────────────────────────────────────────────────────
df = load_customer_360()
products = load_product_stats()

# ══════════════════════════════════════════════════════════════════
#  Customer Profile Lookup
# ══════════════════════════════════════════════════════════════════
section_header("Tra cứu hồ sơ khách hàng")

customer_ids = sorted(df["Customer ID"].unique().tolist())
selected_id = st.selectbox("Chọn Customer ID", customer_ids, key="cust_select")

if selected_id:
    cust = df[df["Customer ID"] == selected_id].iloc[0]

    metric_row([
        {"label": "Customer ID", "value": str(int(cust["Customer ID"]))},
        {"label": "RFM Segment", "value": str(cust.get("rfm_segment", "N/A"))},
        {"label": "Churn Probability", "value": f"{cust.get('churn_probability', 0):.1%}"},
        {"label": "Value Score", "value": f"{cust.get('customer_value_score', 0):.3f}"},
        {"label": "Loyalty Score", "value": f"{cust.get('loyalty_score', 0):.3f}"},
    ])

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        section_header("Hành vi mua sắm")
        behavior_data = {
            "Recency (ngày)": f"{cust.get('recency_days', 0):.0f}",
            "Frequency (90d)": f"{cust.get('frequency_90d', 0)}",
            "Monetary (90d)": f"£{cust.get('monetary_90d', 0):,.2f}",
            "AOV": f"£{cust.get('avg_order_value_90d', 0):,.2f}",
            "Return Rate": f"{cust.get('return_rate_90d', 0):.2%}",
            "Tenure (ngày)": f"{cust.get('tenure_days', 0):.0f}",
        }
        for k, v in behavior_data.items():
            st.markdown(f"**{k}:** {v}")

    with col2:
        section_header("Composite Scores")
        composite_data = {
            "Purchase Intensity": f"{cust.get('purchase_intensity', 0):.4f}",
            "Loyalty Score": f"{cust.get('loyalty_score', 0):.4f}",
            "Retention Score": f"{cust.get('retention_score', 0):.4f}",
            "Customer Value": f"{cust.get('customer_value_score', 0):.4f}",
            "Churn Risk Index": f"{cust.get('churn_risk_index', 0):.4f}",
        }
        for k, v in composite_data.items():
            st.markdown(f"**{k}:** {v}")

    with col3:
        section_header("Cycle Metrics")
        cycle_data = {
            "Median Gap (ngày)": f"{cust.get('cycle_median_gap_days', 0):.1f}",
            "Order Rate Ratio": f"{cust.get('order_rate_ratio', 0):.2f}",
            "Spend Rate Ratio": f"{cust.get('spend_rate_ratio', 0):.2f}",
            "Cycle Risk Score": f"{cust.get('cycle_risk_score', 0):.4f}",
            "At-Risk Bucket": str(cust.get("at_risk_rule_bucket", "N/A")),
        }
        for k, v in cycle_data.items():
            st.markdown(f"**{k}:** {v}")

    # Customer health assessment
    churn_prob = cust.get("churn_probability", 0)
    if churn_prob >= 0.80:
        st.markdown(
            '<div class="danger-box"><strong>Cảnh báo:</strong> Khách hàng này có '
            f'xác suất churn <strong>{churn_prob:.1%}</strong> — cần can thiệp ngay lập tức '
            '(P1 - Urgent Win-back).</div>',
            unsafe_allow_html=True,
        )
    elif churn_prob >= 0.50:
        st.markdown(
            '<div class="warning-box"><strong>Lưu ý:</strong> Khách hàng có '
            f'xác suất churn <strong>{churn_prob:.1%}</strong> — nên gửi email nhắc nhở '
            'kèm voucher nhẹ (P2 - Moderate).</div>',
            unsafe_allow_html=True,
        )
    else:
        success_box(
            f"Khách hàng ổn định (churn probability: <strong>{churn_prob:.1%}</strong>). "
            "Tiếp tục nuôi dưỡng mối quan hệ qua newsletter và sản phẩm mới."
        )

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Lookalike Groups
# ══════════════════════════════════════════════════════════════════
section_header("Nhóm khách hàng tương đồng (Lookalike)")

if selected_id:
    cust_segment = cust.get("rfm_segment", None)
    if cust_segment:
        lookalikes = (
            df[
                (df["rfm_segment"] == cust_segment)
                & (df["Customer ID"] != selected_id)
            ]
            .sort_values("customer_value_score", ascending=False)
            .head(15)
        )

        if len(lookalikes) > 0:
            st.markdown(
                f"Hiển thị **{len(lookalikes)}** khách hàng cùng segment "
                f"**{cust_segment}**, sắp xếp theo Customer Value Score."
            )

            display_cols = [
                "Customer ID", "rfm_segment", "customer_value_score",
                "churn_probability", "frequency_90d", "monetary_90d",
                "recency_days", "loyalty_score",
            ]
            available = [c for c in display_cols if c in lookalikes.columns]
            st.dataframe(
                lookalikes[available].style.format({
                    "customer_value_score": "{:.4f}",
                    "churn_probability": "{:.2%}",
                    "monetary_90d": "£{:,.2f}",
                    "loyalty_score": "{:.4f}",
                }),
                use_container_width=True,
                height=400,
            )

            fig = px.scatter(
                lookalikes,
                x="customer_value_score",
                y="churn_probability",
                size="monetary_90d",
                color="churn_probability",
                color_continuous_scale="RdYlGn_r",
                hover_data=["Customer ID", "frequency_90d"],
                title=f"Lookalike Group: {cust_segment} — Value vs Churn Risk",
            )
            fig.update_layout(
                height=400, template="plotly_white",
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#334155"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có khách hàng tương đồng khác trong segment này.")
    else:
        st.info("Không có thông tin segment cho khách hàng này.")

st.divider()

# ══════════════════════════════════════════════════════════════════
#  Cross-sell / Up-sell Suggestions
# ══════════════════════════════════════════════════════════════════
section_header("Gợi ý sản phẩm Cross-sell / Up-sell")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Sản phẩm phễu (Funnel Products)")
    st.markdown(
        "Sản phẩm **giá trị thấp, dễ quyết định** — phù hợp để kéo khách hàng "
        "at-risk quay lại mua sắm lần đầu:"
    )
    funnel_df = products.copy()
    if "avg_price" in funnel_df.columns and "n_customers" in funnel_df.columns:
        funnel = funnel_df.loc[
            (funnel_df["avg_price"] <= funnel_df["avg_price"].quantile(0.40))
        ].sort_values("n_customers", ascending=False).head(8)
        for i, row in funnel.iterrows():
            st.markdown(f"- **{row['Description']}** — £{row['avg_price']:.2f} "
                        f"({row['n_customers']:,} KH)")

with col2:
    st.markdown("#### Sản phẩm Up-sell (Giá trị cao)")
    st.markdown(
        "Sản phẩm **giá trị cao** dành cho khách hàng loyal/VIP — "
        "tăng giá trị đơn hàng trung bình:"
    )
    if "avg_price" in products.columns:
        upsell = products.loc[
            (products["avg_price"] >= products["avg_price"].quantile(0.70))
        ].sort_values("total_revenue", ascending=False).head(8)
        for i, row in upsell.iterrows():
            st.markdown(f"- **{row['Description']}** — £{row['avg_price']:.2f} "
                        f"(Revenue: £{row['total_revenue']:,.0f})")

insight_box(
    "Chiến lược <strong>Cross-sell</strong> tăng giá trị giỏ hàng bằng cách gợi ý "
    "sản phẩm bổ sung, trong khi <strong>Up-sell</strong> khuyến khích khách hàng "
    "chọn phiên bản cao cấp hơn. Kết hợp cả hai có thể tăng 10–30% AOV.",
    ref="McKinsey: Cross-sell/up-sell đóng góp 35% doanh thu Amazon; "
    "Forrester Research: Product recommendations tăng 10–30% conversion rate."
)
