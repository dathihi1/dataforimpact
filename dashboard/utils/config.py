"""Dashboard configuration constants."""
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_DATA_DIR = PROJECT_ROOT / "data" / "dashboard"

# ── File names ───────────────────────────────────────────────────
CUSTOMER_360_FILE = DASHBOARD_DATA_DIR / "customer_360.csv"
TIME_SERIES_FILE = DASHBOARD_DATA_DIR / "time_series_revenue.csv"
PRODUCT_STATS_FILE = DASHBOARD_DATA_DIR / "product_category_stats.csv"
MODEL_METRICS_FILE = DASHBOARD_DATA_DIR / "model_metrics.json"
WINBACK_FILE = DASHBOARD_DATA_DIR / "winback_playbook.csv"

# ── Colour palette (light-friendly) ─────────────────────────────
COLORS = {
    "primary":    "#3b82f6",   # blue-500
    "secondary":  "#8b5cf6",   # violet-500
    "success":    "#22c55e",   # green-500
    "warning":    "#f59e0b",   # amber-500
    "danger":     "#ef4444",   # red-500
    "accent":     "#f97316",   # orange-500
    "bg_page":    "#f8fafc",   # slate-50
    "bg_card":    "#ffffff",
    "border":     "#e2e8f0",   # slate-200
    "text":       "#1e293b",   # slate-800
    "text_muted": "#64748b",   # slate-500
}

# ── Chart defaults ───────────────────────────────────────────────
CHART_TEMPLATE = "plotly_white"
CHART_COLORS = ["#3b82f6", "#f97316", "#22c55e", "#8b5cf6", "#ef4444", "#06b6d4"]

# ── Segment colour map ───────────────────────────────────────────
SEGMENT_COLORS = {
    "Champions":             "#3b82f6",
    "Loyal":                 "#22c55e",
    "Potential Loyalist":    "#06b6d4",
    "Need Attention":        "#f59e0b",
    "At Risk":               "#f97316",
    "Can't Lose Them":       "#8b5cf6",
    "Hibernating":           "#94a3b8",
    "Lost":                  "#ef4444",
    "VIP/Loyal":             "#22c55e",
    "Bulk/Wholesale":        "#3b82f6",
    "Explorer/Cross-sell Ready": "#8b5cf6",
    "Core Active":           "#06b6d4",
    "At Risk/Churned":       "#ef4444",
    "One-time/Occasional":   "#94a3b8",
    "Watchlist":             "#f59e0b",
    "Low Risk":              "#22c55e",
}

# ── Priority colour map ─────────────────────────────────────────
PRIORITY_COLORS = {
    "P1 - Urgent Win-back":   "#ef4444",
    "P2 - Moderate Win-back": "#f59e0b",
    "P3 - Light Touch":       "#22c55e",
}
