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
    metric_row, inject_custom_css, inject_sidebar_brand, insight_box, success_box,
    section_header,
)
from dashboard.components.charts import pie_chart
from dashboard.components.filters import priority_filter, business_model_filter
from dashboard.utils.config import PRIORITY_COLORS, SEGMENT_COLORS

st.set_page_config(page_title="Win-back Strategy", page_icon="📊", layout="wide")
inject_custom_css()
inject_sidebar_brand()

st.markdown("# Win-back Strategy for At-Risk Customers")
st.caption("Chiến lược can thiệp, mức ưu tiên, và xác suất khách hàng quay lại mua sắm")

st.markdown(
    "Sau khi đã hiểu rõ ai đang có nguy cơ rời bỏ và lý do đằng sau, câu hỏi cuối cùng là: làm gì bây giờ? "
    "Retention Science cho thấy win-back success rate dao động từ 10 đến 40% tùy vào thời điểm can thiệp — "
    "hành động càng sớm, khả năng thành công càng cao vì khách chưa hình thành thói quen mới. "
    "Nhưng không phải mọi khách hàng đều đáng đầu tư ngang nhau: khách giá trị cao rời bỏ sớm "
    "cần ưu tiên khác so với khách đã ngủ đông từ lâu. "
    "Trang này tổng hợp toàn bộ phân tích thành playbook hành động — phân cấp priority, "
    "thông điệp riêng cho B2B và B2C, và ước tính ROI để ra quyết định đầu tư."
)

# ── Data ─────────────────────────────────────────────────────────
wb = load_winback()
df = load_customer_360()

# ── Sidebar Filters ──────────────────────────────────────────────
with st.sidebar:
    st.subheader("Bộ lọc Win-back")
    df = business_model_filter(df, key="wb_bm")
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
section_header("Ma trận chiến lược can thiệp — B2B vs B2C")

tab_b2b, tab_b2c = st.tabs(["B2B / Account-like", "B2C / Consumer-like"])

with tab_b2b:
    st.markdown(
        """
        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
        <thead>
            <tr style="background:#f5f3ff; color:#4c1d95; font-weight:600;">
                <th style="padding:12px; border:1px solid #ddd6fe; text-align:left;">Mức ưu tiên</th>
                <th style="padding:12px; border:1px solid #ddd6fe; text-align:left;">Churn Prob</th>
                <th style="padding:12px; border:1px solid #ddd6fe; text-align:left;">Hành động B2B</th>
                <th style="padding:12px; border:1px solid #ddd6fe; text-align:left;">Kênh</th>
                <th style="padding:12px; border:1px solid #ddd6fe; text-align:left;">Ưu đãi B2B</th>
                <th style="padding:12px; border:1px solid #ddd6fe; text-align:left;">Recovery rate*</th>
            </tr>
        </thead>
        <tbody>
            <tr style="background:#fef2f2;">
                <td style="padding:10px; border:1px solid #ddd6fe;"><strong>P1 - Urgent</strong></td>
                <td style="padding:10px; border:1px solid #ddd6fe;">≥ 80%</td>
                <td style="padding:10px; border:1px solid #ddd6fe;">Account manager gọi điện trực tiếp, review contract, SLA renegotiation</td>
                <td style="padding:10px; border:1px solid #ddd6fe;">Phone + Email + In-person visit</td>
                <td style="padding:10px; border:1px solid #ddd6fe;">Volume discount, Flexible payment terms, Priority shipping</td>
                <td style="padding:10px; border:1px solid #ddd6fe; color:#ef4444;">10–20%</td>
            </tr>
            <tr style="background:#fffbeb;">
                <td style="padding:10px; border:1px solid #ddd6fe;"><strong>P2 - Moderate</strong></td>
                <td style="padding:10px; border:1px solid #ddd6fe;">50–80%</td>
                <td style="padding:10px; border:1px solid #ddd6fe;">Email account review + Giới thiệu sản phẩm mới phù hợp volume</td>
                <td style="padding:10px; border:1px solid #ddd6fe;">Email + LinkedIn + Account portal</td>
                <td style="padding:10px; border:1px solid #ddd6fe;">Tier-based pricing, Auto-replenishment reminder, Early access</td>
                <td style="padding:10px; border:1px solid #ddd6fe; color:#f59e0b;">25–35%</td>
            </tr>
            <tr style="background:#f0fdf4;">
                <td style="padding:10px; border:1px solid #ddd6fe;"><strong>P3 - Light Touch</strong></td>
                <td style="padding:10px; border:1px solid #ddd6fe;">< 50%</td>
                <td style="padding:10px; border:1px solid #ddd6fe;">Newsletter B2B + Báo cáo thị trường + Chương trình loyalty</td>
                <td style="padding:10px; border:1px solid #ddd6fe;">Email newsletter + Account digest</td>
                <td style="padding:10px; border:1px solid #ddd6fe;">Loyalty points, Referral program, Industry insights</td>
                <td style="padding:10px; border:1px solid #ddd6fe; color:#22c55e;">40–55%</td>
            </tr>
        </tbody>
        </table>
        <p style="font-size:0.78rem; color:#64748b; margin-top:8px;">
        * B2B win-back: Bain (2024) — 20–40% recovery nếu can thiệp trong 30 ngày. B2B churn chủ yếu do poor service, không phải giá (Rivo 2026).
        </p>
        """,
        unsafe_allow_html=True,
    )

with tab_b2c:
    st.markdown(
        """
        <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
        <thead>
            <tr style="background:#eff6ff; color:#1d4ed8; font-weight:600;">
                <th style="padding:12px; border:1px solid #bfdbfe; text-align:left;">Mức ưu tiên</th>
                <th style="padding:12px; border:1px solid #bfdbfe; text-align:left;">Churn Prob</th>
                <th style="padding:12px; border:1px solid #bfdbfe; text-align:left;">Hành động B2C</th>
                <th style="padding:12px; border:1px solid #bfdbfe; text-align:left;">Kênh</th>
                <th style="padding:12px; border:1px solid #bfdbfe; text-align:left;">Ưu đãi B2C</th>
                <th style="padding:12px; border:1px solid #bfdbfe; text-align:left;">Recovery rate*</th>
            </tr>
        </thead>
        <tbody>
            <tr style="background:#fef2f2;">
                <td style="padding:10px; border:1px solid #bfdbfe;"><strong>P1 - Urgent</strong></td>
                <td style="padding:10px; border:1px solid #bfdbfe;">≥ 80%</td>
                <td style="padding:10px; border:1px solid #bfdbfe;">Email cá nhân hóa + Voucher mạnh + Survey lý do rời bỏ</td>
                <td style="padding:10px; border:1px solid #bfdbfe;">Email + SMS + Retargeting ads</td>
                <td style="padding:10px; border:1px solid #bfdbfe;">Voucher 20–30%, Free shipping, Gift with purchase</td>
                <td style="padding:10px; border:1px solid #bfdbfe; color:#ef4444;">10–20%</td>
            </tr>
            <tr style="background:#fffbeb;">
                <td style="padding:10px; border:1px solid #bfdbfe;"><strong>P2 - Moderate</strong></td>
                <td style="padding:10px; border:1px solid #bfdbfe;">50–80%</td>
                <td style="padding:10px; border:1px solid #bfdbfe;">Email nhắc chu kỳ mua + Cross-sell gợi ý category tiếp theo</td>
                <td style="padding:10px; border:1px solid #bfdbfe;">Email + Push notification</td>
                <td style="padding:10px; border:1px solid #bfdbfe;">Voucher 10–15%, Gợi ý sản phẩm phễu, Flash sale</td>
                <td style="padding:10px; border:1px solid #bfdbfe; color:#f59e0b;">25–40%</td>
            </tr>
            <tr style="background:#f0fdf4;">
                <td style="padding:10px; border:1px solid #bfdbfe;"><strong>P3 - Light Touch</strong></td>
                <td style="padding:10px; border:1px solid #bfdbfe;">< 50%</td>
                <td style="padding:10px; border:1px solid #bfdbfe;">Newsletter sản phẩm mới + Content marketing + Loyalty points</td>
                <td style="padding:10px; border:1px solid #bfdbfe;">Email newsletter</td>
                <td style="padding:10px; border:1px solid #bfdbfe;">Sản phẩm mới, Content, Loyalty program enrollment</td>
                <td style="padding:10px; border:1px solid #bfdbfe; color:#22c55e;">50–70%</td>
            </tr>
        </tbody>
        </table>
        <p style="font-size:0.78rem; color:#64748b; margin-top:8px;">
        * B2C win-back: InMobi (2023) — Personalized campaigns có conversion rate 3× so với generic. Recovery rate benchmark: Retention Science (2022).
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

    st.caption("Default dựa trên Retention Science (2022) & Bain (2024) benchmarks")
    recovery_rate_p1 = st.slider("Recovery Rate P1 — Urgent (%)", 5, 40, 15, key="rr_p1") / 100
    recovery_rate_p2 = st.slider("Recovery Rate P2 — Moderate (%)", 10, 60, 30, key="rr_p2") / 100
    recovery_rate_p3 = st.slider("Recovery Rate P3 — Light Touch (%)", 30, 80, 52, key="rr_p3") / 100
    avg_ltv_recovered = st.slider("LTV trung bình recovered (£)", 50, 500, 200, key="ltv_rec")
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
    |---|-------|---------------|--------|
    | 1 | [Reichheld (2001) — Bain & Company / HBR](https://hbr.org/2014/10/the-value-of-keeping-the-right-customers) | Tăng 5% retention → +25–95% profit | Justify ROI cho win-back campaign |
    | 2 | [Harvard Business Review](https://hbr.org/2014/10/the-value-of-keeping-the-right-customers) | Acquire cost = 5–25× retain cost | Ưu tiên retention over acquisition |
    | 3 | [Retention Science (2022)](https://www.retentionscience.com/blog/win-back-campaigns/) | Win-back success rate: 10–40% tùy timing — càng sớm càng hiệu quả | Benchmark recovery rate cho P1/P2/P3 |
    | 4 | [McKinsey Digital (2022)](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-value-of-getting-personalization-right) | ML prediction giảm 15–20% churn, personalization tăng 20–30% conversion | Validate Random Forest + cá nhân hóa hành động |
    | 5 | [Kumar & Reinartz (2016) — JAMS](https://link.springer.com/article/10.1007/s11747-016-0488-7) | RFM + CLV là nền tảng CRM — nhóm CLV cao cần ưu tiên ngân sách win-back | Phân loại ưu tiên P1/P2/P3 theo value |
    | 6 | [Gupta & Lehmann (2005) — HBS](https://www.hbs.edu/faculty/Pages/item.aspx?num=19162) | Purchase cycle monitoring = best early detection | Cycle-based at-risk features |
    | 7 | [InMobi (2023) — Personalization](https://www.inmobi.com/resources/reports/personalization) | Personalized campaigns: 3× conversion vs generic messaging | Cá nhân hóa winback_action theo segment |
    | 8 | [Statista (2023)](https://www.statista.com/statistics/816735/customer-churn-rate-by-industry-us/) | E-commerce annual churn: 70–80% — baseline cho ROI calculation | Benchmark churn rate trong ROI calculator |
    | 9 | [Rivo (2026) — B2B Loyalty](https://rivo.io/resources/b2b-loyalty-statistics) | B2B loyalty programs: +82% retention, ROI 4.8× | B2B playbook: account manager + loyalty |
    """
)
