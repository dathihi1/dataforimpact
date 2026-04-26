# 404_Not_Found

## USER BEHAVIOR PREDICTION
This repository contains an end-to-end analytics workflow for identifying at-risk customers, segmenting customer behavior, and generating business-facing recommendation strategies from online retail transaction data.

The current implementation is strongest in three areas:

- customer-level churn and retention features
- dual-track B2B/B2C segmentation and recommendation logic
- an interactive Streamlit dashboard for executive monitoring and win-back analysis

The project uses cleaned transaction data, notebook-based analysis, reusable Python feature builders, unit tests, and a multi-page dashboard to move from raw purchase behavior to operational actions.

## What The Project Does

The repository answers four practical business questions:

1. Which customers are becoming inactive or at risk of churn?
2. Which customer groups behave like consumers versus account-style buyers?
3. What segment-level actions should the business take for retention, cross-sell, upsell, and win-back?
4. How can these insights be monitored in a dashboard instead of only in notebooks?

## Current Implementation Focus

Although the original competition framing references broader topics such as LTV, ROMI, and forecasting, the current codebase is primarily implemented around:

- cleaned transaction analysis
- churn-oriented feature engineering
- RFM and composite customer scoring
- B2B and B2C behavioral segmentation
- recommendation logic grounded in country scope and category affinity
- at-risk customer monitoring through Streamlit

If you want the documentation to match the code that actually runs today, this is the correct scope.

## Repository Structure

```text
404_Not_Found/
|-- data/
|   |-- Year 2009-2010.csv
|   |-- Year 2010-2011.csv
|   |-- cleaned/
|   |   |-- online_retail_cleaned_full.csv
|   |   |-- online_retail_cleaned_returns.csv
|   |   `-- online_retail_cleaned_sales.csv
|   |-- features/
|   |   |-- customer_features.csv
|   |   `-- forecast_features.csv
|   `-- sample/
|       `-- risk_ranking_sample.csv
|-- Notebook/
|   |-- 0_Problems_Definitions.ipynb
|   |-- 01_Data_Understanding.ipynb
|   |-- 02_Data_Cleaning.ipynb
|   |-- 03_EDA.ipynb
|   |-- 04_Start_Implementation.ipynb
|   |-- 05_Feature_Engineering.ipynb
|   |-- 06_segmentation_and_recommendation.ipynb
|   `-- 07_at-risk_prediction.ipynb
|-- dashboard/
|   |-- app.py
|   |-- requirements.txt
|   |-- pages/
|   |   |-- 1_Executive_Overview.py
|   |   |-- 2_Purchasing_Behavior.py
|   |   |-- 3_Product_Recommendation.py
|   |   |-- 4_AtRisk_Identification.py
|   |   |-- 5_AtRisk_DeepDive.py
|   |   `-- 6_Winback_Strategy.py
|   |-- components/
|   `-- utils/
|-- src/
|   |-- data_contract.py
|   |-- risk_scoring.py
|   |-- features/
|   |   |-- churn_feature_builder.py
|   |   `-- composite_feature_builder.py
|   `-- validation/
|       `-- time_split.py
|-- tests/
`-- README.md
```

## Core Analytical Workflow

### 1. Data Cleaning And Validation

The notebooks and source modules assume a cleaned transaction dataset with consistent date parsing, return handling, and customer-level availability.

Key validation surfaces include:

- schema and required-column checks in `src.data_contract`
- notebook-level path resolution so notebooks run correctly from the `Notebook/` directory
- unit tests for feature builders and validation utilities

### 2. Customer Feature Engineering

`src/features/churn_feature_builder.py` creates customer-level behavioral features such as:

- recency
- 90-day frequency and monetary value
- average order value
- return rate
- tenure
- number of active purchase days
- average days between orders
- recency velocity
- churn label

`src/features/composite_feature_builder.py` then derives business-oriented composite features such as:

- purchase intensity
- loyalty score
- retention score
- customer value score
- churn risk index
- quartile-based RFM segment

### 3. Segmentation And Recommendation

`Notebook/06_segmentation_and_recommendation.ipynb` is the main business notebook for:

- splitting customers into `B2B / Account-like` and `B2C / Consumer-like`
- assigning rule-based behavior segments per business model
- running K-Means clustering within each model
- mapping clusters to business personas
- generating recommendation actions

The current recommendation logic is intentionally asymmetric:

- B2B uses product-level cross-sell logic scoped by country bucket
- B2C uses category-level affinity and next-best-category logic

### 4. At-Risk Dashboard

The Streamlit dashboard in `dashboard/app.py` and `dashboard/pages/` turns the analysis into operational views for:

- executive summary
- purchasing behavior
- product recommendation
- at-risk identification
- deep-dive diagnostics
- win-back strategy

## Verified Snapshot Metrics

The following metrics were extracted from the executed segmentation notebook and reflect the current validated state of the repository:

| Metric | Value |
|---|---:|
| Raw transaction rows | 797,885 |
| Raw columns | 28 |
| Customer-level rows in modeling table | 5,581 |
| Snapshot date used for churn labeling | 2011-10-10 12:50:00 |
| Churn rate at snapshot | 62.78% |
| B2B customers | 658 |
| B2C customers | 4,923 |
| B2B share | 11.79% |
| B2C share | 88.21% |

## Environment Setup

### Prerequisites

- Python 3.11 or newer
- PowerShell on Windows if you want to follow the commands exactly as shown below

### 1. Create And Activate A Virtual Environment

```powershell
cd "D:\Data impact\404_Not_Found"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2. Install Dependencies

This repository does not currently expose a single root dependency file for notebooks, tests, and dashboard together, so install the dashboard requirements plus the analysis stack explicitly:

```powershell
pip install -r dashboard/requirements.txt matplotlib seaborn jupyter ipykernel openpyxl pytest
```

This covers the main tools used across:

- notebooks: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, `jupyter`, `ipykernel`, `openpyxl`
- dashboard: `streamlit`, `plotly`
- tests: `pytest`

## How To Run The Project

### Run The Notebooks

Open the repository in VS Code or Jupyter and run the notebooks in sequence:

1. `Notebook/0_Problems_Definitions.ipynb`
2. `Notebook/01_Data_Understanding.ipynb`
3. `Notebook/02_Data_Cleaning.ipynb`
4. `Notebook/03_EDA.ipynb`
5. `Notebook/04_Start_Implementation.ipynb`
6. `Notebook/05_Feature_Engineering.ipynb`
7. `Notebook/06_segmentation_and_recommendation.ipynb`
8. `Notebook/07_at-risk_prediction.ipynb`

The most business-critical notebook at the moment is `Notebook/06_segmentation_and_recommendation.ipynb`.

### Run The Dashboard

```powershell
streamlit run dashboard/app.py
```

### Run The Tests

```powershell
pytest
```

## Main Source Modules

### `src/data_contract.py`

Validates cleaned transactional data before downstream processing.

### `src/features/churn_feature_builder.py`

Builds customer-level churn features from transaction history using a snapshot-date formulation.

### `src/features/composite_feature_builder.py`

Creates normalized composite metrics for loyalty, customer value, retention, and churn risk.

### `src/risk_scoring.py`

Provides a lightweight deterministic risk score interface built around frequency, monetary value, and recency.

## Business Logic Highlights

### B2B Logic

- customers are treated as account-like buyers
- recommendations are scoped by market through country grouping
- the system favors account expansion, replenishment, and account retention language

### B2C Logic

- customers are treated as consumer-like buyers
- recommendations use category affinity instead of SKU pair affinity
- the system emphasizes next-best-category, reactivation, and category cross-sell

## Quality Controls

The segmentation notebook includes explicit QA checks to reduce interpretation errors. These checks validate:

- one row per customer after merges
- preserved customer counts
- segment and cluster share consistency
- non-missing business labels
- valid evidence-source labels for recommendations
- B2B product-level recommendation scope
- B2C category-level recommendation scope

## Known Limitations

- the repository currently mixes notebook-driven workflows with reusable source modules, so orchestration is not yet packaged as a single application pipeline
- there is no unified root dependency file yet
- B2B country-level affinity evidence is much thinner than B2C category-level evidence in the current snapshot
- some broader themes mentioned in the original project framing, such as full ROMI modeling, are not the strongest implemented part of the current codebase

## Recommended Reading

- `Notebook/06_segmentation_and_recommendation.ipynb` for the most complete business logic
- `INSIGHTS.md` for a detailed narrative summary of current analytical findings

## License / Usage Note

This repository appears to have been developed for a Data for Impact competition workflow. Use the assets and interpretations in accordance with your project submission rules and dataset licensing terms.
