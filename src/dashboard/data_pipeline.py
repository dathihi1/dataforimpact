"""
Dashboard Data Pipeline
=======================
Precompute all data needed for the 6-page Streamlit dashboard.
Reads cleaned data, builds features, runs the best churn model,
and exports everything to ``data/dashboard/``.

Usage:
    python -m src.dashboard.data_pipeline
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ── Make sure project root is on sys.path ─────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_contract import run_data_contract_checks
from src.features.churn_feature_builder import build_churn_features
from src.features.composite_feature_builder import build_composite_features

# ── Constants ──────────────────────────────────────────────────────
DATA_DIR = PROJECT_ROOT / "data"
CLEANED_PATH = DATA_DIR / "cleaned" / "online_retail_cleaned_full.csv"
DASHBOARD_DIR = DATA_DIR / "dashboard"
INACTIVITY_DAYS = 60


# ── Helper: build cycle features (ported from notebook 07) ────────
def _build_cycle_features(
    history_df: pd.DataFrame,
    snapshot_date: pd.Timestamp,
) -> pd.DataFrame:
    """Engineer purchase-cycle-based features for each customer."""
    invoice_level = (
        history_df.groupby(["Customer ID", "Invoice"], as_index=False)
        .agg(
            invoice_date=("InvoiceDate", "max"),
            invoice_value=("TotalValue", "sum"),
            invoice_units=("Quantity", "sum"),
        )
    )
    invoice_level["invoice_day"] = invoice_level["invoice_date"].dt.normalize()

    last30_start = snapshot_date - pd.Timedelta(days=30)
    prev60_start = snapshot_date - pd.Timedelta(days=90)
    prev60_end = snapshot_date - pd.Timedelta(days=30)

    cycle_rows: list[dict] = []
    for customer_id, group in invoice_level.groupby("Customer ID"):
        unique_days = np.sort(
            group["invoice_day"].drop_duplicates().values.astype("datetime64[D]")
        )
        if len(unique_days) >= 2:
            gaps = np.diff(unique_days).astype(int)
            cycle_median_gap = float(np.median(gaps))
            cycle_mean_gap = float(np.mean(gaps))
            cycle_std_gap = float(np.std(gaps))
        else:
            gaps = np.array([])
            cycle_median_gap = 0.0
            cycle_mean_gap = 0.0
            cycle_std_gap = 0.0

        cycle_cv = float(cycle_std_gap / cycle_mean_gap) if cycle_mean_gap > 0 else 0.0

        recent_30 = group.loc[group["invoice_date"] > last30_start]
        prev_60 = group.loc[
            (group["invoice_date"] > prev60_start)
            & (group["invoice_date"] <= prev60_end)
        ]

        orders_last30d = int(recent_30["Invoice"].nunique())
        orders_prev60d = int(prev_60["Invoice"].nunique())
        spend_last30d = float(recent_30["invoice_value"].sum())
        spend_prev60d = float(prev_60["invoice_value"].sum())

        prev30_equiv_orders = orders_prev60d / 2 if orders_prev60d > 0 else 0.0
        prev30_equiv_spend = spend_prev60d / 2 if spend_prev60d > 0 else 0.0

        order_rate_ratio = float((orders_last30d + 0.5) / (prev30_equiv_orders + 0.5))
        spend_rate_ratio = float((spend_last30d + 1.0) / (prev30_equiv_spend + 1.0))
        frequency_momentum = float(orders_last30d - prev30_equiv_orders)
        spend_momentum = float(spend_last30d - prev30_equiv_spend)

        cycle_rows.append(
            {
                "Customer ID": customer_id,
                "cycle_median_gap_days": cycle_median_gap,
                "cycle_mean_gap_days": cycle_mean_gap,
                "cycle_std_gap_days": cycle_std_gap,
                "cycle_cv": cycle_cv,
                "orders_last30d": orders_last30d,
                "orders_prev60d": orders_prev60d,
                "spend_last30d": spend_last30d,
                "spend_prev60d": spend_prev60d,
                "order_rate_ratio": order_rate_ratio,
                "spend_rate_ratio": spend_rate_ratio,
                "frequency_momentum": frequency_momentum,
                "spend_momentum": spend_momentum,
            }
        )

    return pd.DataFrame(cycle_rows)


# ── Helper: at-risk rule scoring (ported from notebook 07) ────────
def _apply_atrisk_rules(model_df: pd.DataFrame) -> pd.DataFrame:
    """Apply rule-based at-risk scoring and buckets."""
    model_df["at_risk_rule_score"] = 0
    model_df["at_risk_rule_score"] += (
        model_df["recency_vs_expected_gap"].fillna(0) >= 1.2
    ).astype(int)
    model_df["at_risk_rule_score"] += (
        model_df["recency_vs_expected_gap"].fillna(0) >= 1.8
    ).astype(int)
    model_df["at_risk_rule_score"] += (model_df["order_rate_ratio"].fillna(1) < 0.75).astype(int)
    model_df["at_risk_rule_score"] += (model_df["spend_rate_ratio"].fillna(1) < 0.80).astype(int)
    model_df["at_risk_rule_score"] += (model_df["recency_days"].fillna(0) >= 90).astype(int)
    model_df["at_risk_rule_score"] += (model_df["frequency_90d"].fillna(0) <= 1).astype(int)

    model_df["at_risk_rule_bucket"] = pd.cut(
        model_df["at_risk_rule_score"],
        bins=[-0.1, 1, 3, 6],
        labels=["Low Risk", "Watchlist", "At Risk"],
    )
    return model_df


# ── Helper: build preprocessor for ML ────────────────────────────
def _make_preprocessor(
    numeric_features: list[str],
    categorical_features: list[str],
    scale_numeric: bool,
) -> ColumnTransformer:
    numeric_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scaler", StandardScaler()))

    return ColumnTransformer(
        transformers=[
            ("num", Pipeline(numeric_steps), numeric_features),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ],
        remainder="drop",
    )


# ── Helper: tune threshold for recall ────────────────────────────
def _tune_threshold(y_true, y_prob):
    """Tune threshold to maximize expected business value.
    TP Value: 100, FP Cost: 10, FN Cost: 50.
    """
    rows = []
    v_tp, c_fp, c_fn = 100, 10, 50
    for threshold in np.linspace(0.10, 0.90, 81):
        pred = (y_prob >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
        expected_value = (tp * v_tp) - (fp * c_fp) - (fn * c_fn)
        rows.append(
            {
                "threshold": threshold,
                "accuracy": accuracy_score(y_true, pred),
                "precision": precision_score(y_true, pred, zero_division=0),
                "recall": recall_score(y_true, pred, zero_division=0),
                "f1": f1_score(y_true, pred, zero_division=0),
                "expected_value": expected_value,
            }
        )
    df = pd.DataFrame(rows)
    best = df.sort_values("expected_value", ascending=False).iloc[0]
    return float(best["threshold"])


# ── Helper: win-back playbook (ported from notebook 07) ───────────
def _build_winback_playbook(
    model_df: pd.DataFrame,
    raw_df: pd.DataFrame,
    snapshot_date: pd.Timestamp,
) -> pd.DataFrame:
    """Create win-back playbook with intervention priority & actions."""
    # Top funnel products (low price, high frequency)
    sales = raw_df.loc[
        (raw_df["Quantity"] > 0) & (raw_df["InvoiceDate"] <= snapshot_date)
    ].copy()

    product_stats = (
        sales.groupby("Description")
        .agg(
            total_qty=("Quantity", "sum"),
            avg_price=("Price", "mean"),
            n_customers=("Customer ID", "nunique"),
        )
        .reset_index()
    )
    funnel_products = product_stats.loc[
        (product_stats["avg_price"] <= product_stats["avg_price"].quantile(0.30))
        & (product_stats["n_customers"] >= product_stats["n_customers"].quantile(0.50))
    ]
    funnel_list = ", ".join(funnel_products["Description"].head(5).tolist())

    # Last product purchased per customer
    last_purchase = (
        sales.sort_values("InvoiceDate")
        .groupby("Customer ID")
        .agg(
            last_product=("Description", "last"),
            last_category=("StockCode", "last"),
        )
        .reset_index()
    )

    # Build playbook
    at_risk_mask = (model_df["churn_predicted"] == 1) | (
        model_df["at_risk_rule_bucket"].isin(["Watchlist", "At Risk"])
    )
    playbook = model_df[at_risk_mask][
        [
            "Customer ID",
            "churn_probability",
            "at_risk_rule_bucket",
            "cycle_risk_score",
            "recency_vs_expected_gap",
            "rfm_segment",
            "customer_value_score",
        ]
    ].copy()

    playbook = playbook.merge(last_purchase, on="Customer ID", how="left")
    playbook["last_product"] = playbook["last_product"].fillna("Unknown Product")
    playbook["funnel_products"] = funnel_list

    # Intervention priority
    def _assign_priority(row):
        prob = row["churn_probability"]
        if prob >= 0.80:
            return "P1 - Urgent Win-back"
        elif prob >= 0.50:
            return "P2 - Moderate Win-back"
        else:
            return "P3 - Light Touch"

    playbook["intervention_priority"] = playbook.apply(_assign_priority, axis=1)

    # Win-back action
    def _assign_action(row):
        priority = row["intervention_priority"]
        if "P1" in priority:
            return "Email chăm sóc + voucher mạnh + nhắc đúng chu kỳ mua"
        elif "P2" in priority:
            return "Email nhắc nhở + voucher nhẹ + gợi ý sản phẩm phễu"
        else:
            return "Gợi ý sản phẩm mới qua newsletter"

    playbook["winback_action"] = playbook.apply(_assign_action, axis=1)

    return playbook.sort_values("churn_probability", ascending=False)


# ── Helper: B2B/B2C classification (ported from notebook 06) ─────
def _classify_b2b_b2c(customer_360: pd.DataFrame) -> pd.DataFrame:
    """Classify customers as B2B/Account-like or B2C/Consumer-like and
    assign behaviour segments within each group."""
    df = customer_360.copy()

    # Quantile thresholds for B2B signal detection
    aov_q85 = df["avg_order_value_90d"].quantile(0.85)
    monetary_q90 = df["monetary_90d"].quantile(0.90)
    units_invoice_q85 = df["avg_units_per_invoice_90d"].quantile(0.85)
    units_invoice_q90 = df["avg_units_per_invoice_90d"].quantile(0.90)
    units_total_q90 = df["total_units_90d"].quantile(0.90)
    products_q75 = df["distinct_products_90d"].quantile(0.75)
    invoices_q80 = df["distinct_invoices_90d"].quantile(0.80)
    value_q80 = df["customer_value_score"].quantile(0.80)
    value_q85 = df["customer_value_score"].quantile(0.85)
    loyalty_q75 = df["loyalty_score"].quantile(0.75)
    churn_q75 = df["churn_risk_index"].quantile(0.75)
    recency_q80 = df["recency_days"].quantile(0.80)

    def _assign_customer_model(row: pd.Series) -> str:
        b2b_signals = 0
        if row["avg_units_per_invoice_90d"] >= units_invoice_q90:
            b2b_signals += 1
        if row["total_units_90d"] >= units_total_q90:
            b2b_signals += 1
        if row["avg_order_value_90d"] >= aov_q85:
            b2b_signals += 1
        if row["monetary_90d"] >= monetary_q90 and row["distinct_invoices_90d"] >= invoices_q80:
            b2b_signals += 1
        return "B2B / Account-like" if b2b_signals >= 2 else "B2C / Consumer-like"

    def _assign_b2c_segment(row: pd.Series) -> str:
        if (
            row["customer_value_score"] >= value_q80
            and row["loyalty_score"] >= loyalty_q75
            and row["recency_days"] <= 30
        ):
            return "VIP / Loyal"
        if row["frequency_90d"] <= 1 and row["n_unique_days"] <= 1:
            return "One-time / Occasional"
        if row["churn_risk_index"] >= churn_q75 or row["rfm_segment"] in {
            "At Risk", "Can't Lose Them", "Lost", "Hibernating"
        }:
            return "At Risk / Churned"
        if row["distinct_products_90d"] >= products_q75 and row["frequency_90d"] >= 2:
            return "Explorer / Cross-sell Ready"
        return "Core Active"

    def _assign_b2b_segment(row: pd.Series) -> str:
        if (
            row["customer_value_score"] >= value_q85
            and row["monetary_90d"] >= monetary_q90
            and row["distinct_invoices_90d"] >= invoices_q80
        ):
            return "Key Account / Strategic"
        if row["avg_units_per_invoice_90d"] >= units_invoice_q85 or row["total_units_90d"] >= units_total_q90:
            return "Bulk / Wholesale"
        if row["churn_risk_index"] >= churn_q75 or row["recency_days"] >= recency_q80:
            return "At Risk Account"
        return "Transactional Account"

    df["customer_model"] = df.apply(_assign_customer_model, axis=1)
    df["behavior_segment"] = df.apply(
        lambda row: (
            _assign_b2b_segment(row)
            if row["customer_model"] == "B2B / Account-like"
            else _assign_b2c_segment(row)
        ),
        axis=1,
    )
    return df


# ══════════════════════════════════════════════════════════════════
#  MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════
def run_pipeline() -> None:
    """Execute the full data pipeline and write outputs to data/dashboard/."""
    import warnings
    warnings.filterwarnings("ignore")

    print("=" * 60)
    print("Dashboard Data Pipeline")
    print("=" * 60)

    # ── 1. Load & validate ────────────────────────────────────────
    print("\n[1/8] Loading cleaned data …")
    raw_df = pd.read_csv(CLEANED_PATH, parse_dates=["InvoiceDate"])
    contract = run_data_contract_checks(raw_df)
    print(f"   Rows: {contract['rows']:,}  Columns: {contract['columns']}")
    print(f"   Date range: {contract['date_min']}  →  {contract['date_max']}")

    max_date = raw_df["InvoiceDate"].max()
    snapshot_date = max_date - pd.Timedelta(days=INACTIVITY_DAYS)
    print(f"   Snapshot: {snapshot_date}")

    # ── 2. Build features ─────────────────────────────────────────
    print("\n[2/8] Building churn & composite features …")
    churn_features = build_churn_features(
        raw_df, snapshot_date=snapshot_date, inactivity_days=INACTIVITY_DAYS
    )
    composite_features = build_composite_features(churn_features)
    print(f"   Customer feature table: {composite_features.shape}")

    # ── 3. Build cycle features ───────────────────────────────────
    print("\n[3/8] Building cycle-based features …")
    sales_df = raw_df.loc[raw_df["Quantity"] > 0].copy()
    history_df = sales_df.loc[sales_df["InvoiceDate"] <= snapshot_date].copy()
    cycle_features = _build_cycle_features(history_df, snapshot_date)

    model_df = composite_features.merge(cycle_features, on="Customer ID", how="left")

    # Expected cycle & derived metrics
    cycle_gap_fallback = model_df["avg_days_between_orders"].fillna(0).clip(lower=0)
    model_df["expected_cycle_days"] = np.where(
        model_df["cycle_median_gap_days"].fillna(0) > 0,
        model_df["cycle_median_gap_days"],
        cycle_gap_fallback,
    )
    model_df["expected_cycle_days"] = pd.Series(
        model_df["expected_cycle_days"]
    ).replace(0, 30.0)
    model_df["recency_vs_expected_gap"] = (
        model_df["recency_days"] / model_df["expected_cycle_days"]
    )
    model_df["days_past_expected_gap"] = (
        model_df["recency_days"] - model_df["expected_cycle_days"]
    )
    model_df["cycle_break_flag"] = (
        model_df["recency_vs_expected_gap"] >= 1.5
    ).astype(int)

    # Cycle risk score
    recency_c = np.clip(model_df["recency_vs_expected_gap"].fillna(0) / 2.5, 0, 1)
    freq_c = np.clip((1.0 - model_df["order_rate_ratio"].fillna(1)) / 1.5, 0, 1)
    spend_c = np.clip((1.0 - model_df["spend_rate_ratio"].fillna(1)) / 1.5, 0, 1)
    model_df["cycle_risk_score"] = (
        0.5 * recency_c + 0.3 * freq_c + 0.2 * spend_c
    ).round(4)

    # At-risk rule scoring
    model_df = _apply_atrisk_rules(model_df)
    model_df = model_df.replace([np.inf, -np.inf], np.nan)
    print(f"   Model-ready table: {model_df.shape}")

    # ── 4. Train best model (Random Forest) ───────────────────────
    print("\n[4/8] Training Random Forest churn model …")
    base_numeric = [
        "recency_days", "frequency_90d", "monetary_90d", "avg_order_value_90d",
        "return_rate_90d", "tenure_days", "n_unique_days", "avg_days_between_orders",
        "day_of_week_mode", "recency_velocity",
    ]
    composite_numeric = [
        "purchase_intensity", "loyalty_score", "retention_score",
        "customer_value_score", "churn_risk_index",
    ]
    cycle_numeric = [
        "cycle_median_gap_days", "cycle_mean_gap_days", "cycle_std_gap_days",
        "cycle_cv", "orders_last30d", "orders_prev60d", "spend_last30d",
        "spend_prev60d", "order_rate_ratio", "spend_rate_ratio",
        "frequency_momentum", "spend_momentum", "expected_cycle_days",
        "recency_vs_expected_gap", "days_past_expected_gap",
        "cycle_break_flag", "cycle_risk_score", "at_risk_rule_score",
    ]
    cat_features = ["rfm_segment", "at_risk_rule_bucket"]
    all_numeric = base_numeric + composite_numeric + cycle_numeric
    full_features = all_numeric + cat_features

    y = model_df["churn_label"].astype(int)
    train_df, temp_df = train_test_split(
        model_df, test_size=0.40, stratify=y, random_state=42,
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, stratify=temp_df["churn_label"], random_state=42,
    )

    preprocessor = _make_preprocessor(all_numeric, cat_features, scale_numeric=False)
    rf_base = RandomForestClassifier(
        n_estimators=350,
        max_depth=None,
        min_samples_leaf=5,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )
    calibrated_rf = CalibratedClassifierCV(rf_base, method='isotonic', cv=3)
    rf_model = Pipeline(
        [
            ("prep", preprocessor),
            ("model", calibrated_rf),
        ]
    )
    rf_model.fit(train_df[full_features], train_df["churn_label"])

    # Threshold tuning on val set
    val_prob = rf_model.predict_proba(val_df[full_features])[:, 1]
    best_threshold = _tune_threshold(val_df["churn_label"], val_prob)

    # Evaluate on test set
    test_prob = rf_model.predict_proba(test_df[full_features])[:, 1]
    test_pred = (test_prob >= best_threshold).astype(int)
    metrics = {
        "model": "Random Forest",
        "threshold": round(best_threshold, 4),
        "accuracy": round(accuracy_score(test_df["churn_label"], test_pred), 4),
        "precision": round(
            precision_score(test_df["churn_label"], test_pred, zero_division=0), 4
        ),
        "recall": round(
            recall_score(test_df["churn_label"], test_pred, zero_division=0), 4
        ),
        "f1": round(f1_score(test_df["churn_label"], test_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(test_df["churn_label"], test_prob), 4),
        "pr_auc": round(average_precision_score(test_df["churn_label"], test_prob), 4),
        "brier_score": round(brier_score_loss(test_df["churn_label"], test_prob), 4),
    }
    print(f"   Threshold: {metrics['threshold']}")
    print(
        f"   Test  →  Acc: {metrics['accuracy']}  Prec: {metrics['precision']}  "
        f"Rec: {metrics['recall']}  F1: {metrics['f1']}  AUC: {metrics['roc_auc']}"
    )

    # Score *all* customers
    all_prob = rf_model.predict_proba(model_df[full_features])[:, 1]
    model_df["churn_probability"] = all_prob.round(4)
    model_df["churn_predicted"] = (all_prob >= best_threshold).astype(int)

    # ── 5. Build behavior aggregates ──────────────────────────────
    print("\n[5/8] Building behavior aggregates …")
    window_start = snapshot_date - pd.Timedelta(days=89)
    sales_history = sales_df.loc[
        (sales_df["InvoiceDate"] >= window_start)
        & (sales_df["InvoiceDate"] <= snapshot_date)
    ].copy()

    customer_behavior = (
        sales_history.groupby("Customer ID")
        .agg(
            total_units_90d=("Quantity", "sum"),
            avg_units_per_line_90d=("Quantity", "mean"),
            distinct_products_90d=("StockCode", "nunique"),
            distinct_invoices_90d=("Invoice", "nunique"),
            latest_country=("Country", "last"),
        )
        .reset_index()
    )

    invoice_units = (
        sales_history.groupby(["Customer ID", "Invoice"], as_index=False)
        .agg(invoice_units=("Quantity", "sum"))
    )
    invoice_units_summary = (
        invoice_units.groupby("Customer ID", as_index=False)
        .agg(
            avg_units_per_invoice_90d=("invoice_units", "mean"),
            max_units_per_invoice_90d=("invoice_units", "max"),
        )
    )

    customer_360 = (
        model_df.merge(customer_behavior, on="Customer ID", how="left")
        .merge(invoice_units_summary, on="Customer ID", how="left")
    )
    fill_zero = [
        "total_units_90d", "avg_units_per_line_90d", "distinct_products_90d",
        "distinct_invoices_90d", "avg_units_per_invoice_90d",
        "max_units_per_invoice_90d",
    ]
    customer_360[fill_zero] = customer_360[fill_zero].fillna(0)
    customer_360["latest_country"] = customer_360["latest_country"].fillna("Unknown")

    # ── 5b. Classify B2B / B2C ─────────────────────────────────────
    print("\n[5b/8] Classifying B2B / B2C …")
    customer_360 = _classify_b2b_b2c(customer_360)
    b2b_count = int((customer_360["customer_model"] == "B2B / Account-like").sum())
    b2c_count = int((customer_360["customer_model"] == "B2C / Consumer-like").sum())
    print(f"   B2B: {b2b_count}  B2C: {b2c_count}")

    # ── 6. Build time-series revenue ──────────────────────────────
    print("\n[6/8] Building time-series data …")
    monthly_revenue = (
        sales_df.assign(month=sales_df["InvoiceDate"].dt.to_period("M"))
        .groupby("month")
        .agg(
            revenue=("TotalValue", "sum"),
            orders=("Invoice", "nunique"),
            customers=("Customer ID", "nunique"),
        )
        .reset_index()
    )
    monthly_revenue["month"] = monthly_revenue["month"].dt.to_timestamp()
    monthly_revenue["aov"] = monthly_revenue["revenue"] / monthly_revenue["orders"]

    # Product category stats
    product_stats = (
        sales_df.groupby("Description")
        .agg(
            total_revenue=("TotalValue", "sum"),
            total_qty=("Quantity", "sum"),
            n_customers=("Customer ID", "nunique"),
            avg_price=("Price", "mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
        .head(50)
    )

    # ── 8. Build win-back playbook ────────────────────────────────
    print("\n[8/8] Building win-back playbook …")
    winback = _build_winback_playbook(model_df, raw_df, snapshot_date)

    # ══════════════════════════════════════════════════════════════
    #  EXPORT
    # ══════════════════════════════════════════════════════════════
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)

    customer_360.to_csv(DASHBOARD_DIR / "customer_360.csv", index=False)
    monthly_revenue.to_csv(DASHBOARD_DIR / "time_series_revenue.csv", index=False)
    product_stats.to_csv(DASHBOARD_DIR / "product_category_stats.csv", index=False)
    winback.to_csv(DASHBOARD_DIR / "winback_playbook.csv", index=False)

    with open(DASHBOARD_DIR / "model_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n✅  Pipeline complete!  Outputs in:", DASHBOARD_DIR)
    for p in sorted(DASHBOARD_DIR.iterdir()):
        print(f"   • {p.name}")


if __name__ == "__main__":
    run_pipeline()
