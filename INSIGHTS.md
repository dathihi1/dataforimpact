# Detailed Project Insights

## Purpose Of This Document

This document explains what the project is currently doing, what the validated numbers say, and how the business logic should be interpreted today.

It is intentionally grounded in the executed notebook state rather than in the broader original ambition of the repository. The goal is to keep business interpretation aligned with the code and the verified outputs.

## 1. Executive Summary

The current repository is best understood as a customer analytics system for online retail with four tightly connected layers:

1. cleaned transaction preparation
2. customer-level churn and value feature engineering
3. B2B/B2C segmentation and recommendation design
4. at-risk customer monitoring through a Streamlit dashboard

The strongest implemented business use case is not generic forecasting. It is operational customer management:

- identifying who is at risk
- understanding how customers behave
- deciding what action to take next

## 2. Verified Data Snapshot

The metrics below were extracted from the executed segmentation notebook and should be treated as the current validated baseline for documentation.

| Metric | Value |
|---|---:|
| Raw transaction rows | 797,885 |
| Raw columns | 28 |
| Customer-level modeling rows | 5,581 |
| Snapshot date | 2011-10-10 12:50:00 |
| Churn rate | 62.78% |
| B2B customers | 658 |
| B2C customers | 4,923 |
| B2B share | 11.79% |
| B2C share | 88.21% |

### What These Numbers Mean

- The analytical unit of the business logic is the customer, not the invoice.
- The snapshot-based churn framing is severe: 62.78% of customers are labeled churned under the current inactivity rule and snapshot window.
- The customer base is predominantly B2C-like, so consumer logic should remain the default operating layer.
- B2B is a minority but still strategically important because it concentrates higher account-style purchase behavior.

## 3. Pipeline Interpretation

### 3.1 Data Preparation

The project starts from transaction-level data and moves toward a customer-level modeling table.

Key preparation concepts:

- positive sales and returns are handled explicitly
- dates are transformed into reusable time features
- customer purchase history is compressed into a modeling snapshot
- downstream logic relies on cleaned files in `data/cleaned/`

### 3.2 Churn Features

The churn feature builder creates the behavioral foundation of the project. The most important variables are:

- `recency_days`: how long since the last purchase
- `frequency_90d`: recent purchase intensity
- `monetary_90d`: recent spend
- `avg_order_value_90d`: average ticket size
- `return_rate_90d`: return pressure
- `tenure_days`: customer age in the system
- `n_unique_days`: number of active purchase days
- `avg_days_between_orders`: purchase rhythm
- `recency_velocity`: recency relative to tenure
- `churn_label`: whether future activity appears within the inactivity window

This is a practical feature design because it balances three business views at the same time:

- value
- activity
- risk

### 3.3 Composite Features

The composite feature layer turns raw behavior into more readable business scores:

- `loyalty_score`
- `retention_score`
- `customer_value_score`
- `churn_risk_index`
- `rfm_segment`

These scores simplify later notebook logic because they allow both manual segmentation and cluster interpretation without repeatedly re-deriving the same ideas.

## 4. Business Model Split: B2B vs B2C

The segmentation notebook now explicitly separates two business models before downstream recommendation logic is applied.

### Current Split

| Model | Customers | Share |
|---|---:|---:|
| B2B / Account-like | 658 | 11.79% |
| B2C / Consumer-like | 4,923 | 88.21% |

### Why This Split Matters

Without the split, the project would mix two very different buying patterns:

- consumer-style basket expansion and repeat purchase behavior
- account-style replenishment, volume buying, and retention management

Keeping these flows separate reduces business confusion and prevents the recommendation logic from suggesting the wrong intervention style.

## 5. Segment Distribution Insights

The current notebook output shows the following segment distribution.

### B2C Segments

| Segment | Customers |
|---|---:|
| Core Active | 1,568 |
| One-time / Occasional | 1,302 |
| At Risk / Churned | 1,161 |
| Explorer / Cross-sell Ready | 722 |
| VIP / Loyal | 170 |

### B2B Segments

| Segment | Customers |
|---|---:|
| Key Account / Strategic | 504 |
| Bulk / Wholesale | 151 |
| Transactional Account | 3 |

### Interpretation

#### B2C

- `Core Active` is the largest B2C segment, which means the business has a sizable base of still-engaged consumers to protect and expand.
- `One-time / Occasional` is also large, indicating weak second-purchase conversion remains an important business problem.
- `At Risk / Churned` is materially large, which is consistent with the high snapshot churn rate and supports a strong win-back agenda.
- `VIP / Loyal` is small relative to the total base, so premium retention actions should be highly targeted rather than broad.

#### B2B

- The B2B side is dominated by `Key Account / Strategic`, suggesting that once customers are classified as account-like, the rule set tends to recognize strong commercial value.
- `Bulk / Wholesale` is present but smaller, meaning some account-like buyers are driven more by volume than by broader strategic value.
- `Transactional Account` is almost absent, which is analytically useful: it suggests the current thresholds create a relatively concentrated B2B definition.

This is an insight and a limitation at the same time. It means the current B2B rules may be appropriately strict, but they may also be compressing mid-tier account behavior into a smaller number of labels.

## 6. Country-Specific B2B Insight

The B2B recommendation flow is now market-aware.

### Current B2B Country Scope

| Country Scope | Customers |
|---|---:|
| United Kingdom | 569 |
| Other International | 66 |
| Germany | 23 |

### Interpretation

- The United Kingdom dominates B2B account-like customers in the current snapshot.
- Germany is the only explicitly preserved non-UK market bucket at the current threshold.
- The rest of international demand is too fragmented to support highly granular country-specific logic without creating unstable outputs.

### Business Implication

If the team wants deeper B2B market strategy, the next version should not simply add more countries by default. It should first define business thresholds for when a country deserves its own commercial playbook.

## 7. Recommendation System Insight

The recommendation system is no longer one generic engine.

### 7.1 B2B Recommendation Logic

B2B recommendations operate at product level and are scoped by country bucket.

Current B2B recommendation evidence distribution:

| Evidence Source | Customers |
|---|---:|
| country_segment_top_seller | 651 |
| country_affinity_pair | 7 |

### Interpretation

- True country-specific product-pair evidence exists, but it is very sparse.
- Most B2B recommendations currently rely on top-seller logic within country and segment rather than strong pair-level co-purchase evidence.

This is a realistic outcome, not a failure. Account-like data often becomes sparse once you slice by both market and product basket.

### Business Reading

For B2B, the recommendation engine is better understood as a country-aware commercial prioritization layer than as a classical retail recommender.

It is strongest for:

- replenishment reminders
- country-specific assortment reinforcement
- account expansion suggestions

It is weaker for:

- precise product-pair discovery at small market slices

### 7.2 B2C Recommendation Logic

B2C recommendations now use category-level logic rather than product-pair logic.

Current B2C recommendation evidence distribution:

| Evidence Source | Customers |
|---|---:|
| category_affinity | 4,862 |
| segment_next_best_category | 61 |

### Interpretation

- Category-level affinity is strong enough to support most B2C recommendations directly.
- Only a small minority of B2C customers require fallback to segment-level next-best-category.

This is a much healthier signal structure than the earlier product-pair approach, because it aligns with consumer behavior at a more stable level of abstraction.

### Business Reading

For B2C, the recommendation engine now behaves like a category expansion system.

That makes it useful for:

- basket expansion
- second-purchase conversion
- reactivation with simpler category entry points
- personalized campaign framing around category adjacency rather than exact SKU similarity

## 8. Recommendation Type Distribution

| Recommendation Type | Customers |
|---|---:|
| Repeat-purchase reminder | 2,060 |
| Category cross-sell / Up-sell | 1,475 |
| Category reactivation | 1,388 |
| Account expansion / Upsell | 533 |
| Account replenishment reminder | 123 |
| Business personalization | 2 |

### Interpretation

- Repeat-purchase reminder is the single largest action type. This reinforces the importance of purchase-cycle monitoring in the business strategy.
- Category cross-sell and category reactivation together cover a large B2C population, which means consumer growth should be framed more as guided category movement than product-level pair selling.
- B2B action types are fewer and more concentrated, which is consistent with an account-management operating model.

## 9. Dashboard Insight

The dashboard structure reflects the operational intent of the repository. The six pages map naturally to business consumption:

1. Executive Overview
2. Purchasing Behavior
3. Product Recommendation
4. At-Risk Identification
5. At-Risk Deep Dive
6. Win-back Strategy

This is useful because it means the repository is not only a modeling exercise. It already has a presentation surface for stakeholders.

## 10. What The QA Checks Protect Against

The notebook now includes consistency checks to reduce silent analytical errors.

The QA layer confirms:

- one customer stays one row after repeated merges
- customer counts are preserved
- shares sum correctly within segment and cluster summaries
- market scope and recommendation evidence labels are populated
- B2B stays product-level
- B2C stays category-level

This matters because notebooks are vulnerable to rerun issues, especially when columns are repeatedly merged into the same in-memory DataFrame.

## 11. Risks And Limitations

### 11.1 B2B Evidence Sparsity

Only 7 B2B customers currently receive true `country_affinity_pair` evidence, while 651 rely on `country_segment_top_seller` fallback.

This means the B2B recommendation engine is directionally useful but should not be oversold as a highly personalized pair-mining system.

### 11.2 Segment Concentration In B2B

The B2B segmentation output is heavily concentrated in `Key Account / Strategic` and `Bulk / Wholesale`.

This could mean either:

- the rules are correctly identifying strong account behavior
- or the thresholds are too aggressive and leave little room for mid-tier account nuance

### 11.3 Snapshot Sensitivity

The current churn label depends on a single snapshot date and inactivity window. Business interpretation should remember that churn here is operationally defined, not a universal truth.

### 11.4 Repository Scope Drift

The older project story mentions LTV, ROMI, and forecasting more prominently than the current executable workflow. The implemented core is currently stronger in churn analytics, segmentation, and recommendation.

## 12. Recommended Next Steps

### Priority 1

Formalize the environment into one root dependency file so notebooks, tests, and dashboard share a reproducible setup path.

### Priority 2

Review B2B threshold design to decide whether more countries should receive dedicated market buckets.

### Priority 3

Calibrate the B2B recommendation logic with richer account-level commercial signals if available, such as margin, replenishment criticality, or sales ownership.

### Priority 4

Extend B2C category logic from next-best-category into ranked campaign bundles, not just category suggestions.

## 13. Bottom Line

The project is currently most credible as a customer risk and actioning system.

Its strongest business story is:

- build reliable customer features
- separate B2B from B2C early
- interpret risk and value through segment logic
- recommend the next action in business language
- surface those insights through a dashboard

That story is now consistent with the code, the notebook outputs, and the validated metrics.