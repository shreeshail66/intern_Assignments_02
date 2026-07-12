# Task 1 — Data Analysis and Visualization
**DevRise Internship Program | Batch 1 (2026) | Domain: AI & ML**

## 1. Project Overview

This project performs end-to-end data cleaning, exploratory analysis, and visualization
on a retail sales dataset (3,040 raw order-level records). The raw dataset intentionally
mirrors real-world data quality issues — missing values, duplicate rows, inconsistent text
formatting, mixed/incorrect data types, invalid negative quantities, and price outliers —
so that the full preprocessing pipeline required by the task is genuinely exercised.

The deliverable is a fully documented Jupyter Notebook that:
- Loads and audits the raw data
- Cleans and preprocesses it using **pandas** and **numpy**
- Computes descriptive statistics and business-level aggregates
- Produces 10 expressive visualizations using **matplotlib** and **seaborn**
- Summarizes actionable business insights

## 2. Project Structure

```
devrise-task1/
├── README.md
├── generate_data.py                
├── build_notebook.py               
├── data/
│
├── notebooks/
│   
└── visuals/

```

## 3. Dataset

`data/raw_retail_sales.csv` contains 3,040 retail order records with the following columns:

| Column | Description |
|---|---|
| OrderID | Unique order identifier |
| OrderDate | Date of order (mixed formats in raw data) |
| Region | Sales region (North/South/East/West/Central) |
| Category | Product category |
| SalesChannel | Online or In-Store |
| PaymentMode | Payment method used |
| Quantity | Units purchased |
| UnitPrice | Price per unit (₹) |
| DiscountPercent | Discount applied (%) |
| CustomerAge | Age of customer |
| CustomerRating | Customer satisfaction rating (1–5) |
| TotalSales | Total order value (₹) |

## 4. Setup Instructions

### Requirements
- Python 3.10+
- Jupyter Notebook / JupyterLab

### Installation

```bash
pip install pandas numpy matplotlib seaborn jupyter
```

### Running the project

```bash
python generate_data.py

jupyter notebook notebooks/Task1_Data_Analysis_Visualization.ipynb

```

Running the notebook will regenerate `data/cleaned_retail_sales.csv` and all PNG charts in
`visuals/`.

## 5. Methodology

### 5.1 Data Cleaning (Section 3 of the notebook)
1. Removed exact duplicate rows
2. Standardized text fields (trimmed whitespace, unified casing)
3. Parsed three different date string formats into a single `datetime64` column
4. Coerced numeric columns that were stored as mixed strings/floats into proper numeric dtypes
5. Corrected invalid negative quantities and capped extreme price outliers using the IQR rule
6. Imputed missing numeric values with the **median** (robust to skew) and missing
   categorical values with the **mode**
7. Dropped the small number of rows with unparseable dates
8. Engineered derived features: `OrderMonth`, `OrderWeekday`, `AgeGroup`

### 5.2 Analysis (Section 4)
Descriptive statistics (`.describe()`), revenue aggregation by category/region/month, and
summary business metrics (total revenue, average/median order value).

### 5.3 Visualization (Section 5)
10 charts covering trend (line), category/region comparison (bar, stacked bar), distribution
(histogram, boxplot), relationships (correlation heatmap, scatter), and composition (pie
chart) — each exported as a high-resolution (300 DPI) `.png`.

### 5.4 Business Insights (Section 6)
A written summary translating the charts into concrete business recommendations
(see the final section of the notebook).

## 6. Key Results

- Cleaned dataset: **0 missing values, 0 duplicate rows**, fully consistent dtypes
- 10 high-resolution visualizations exported to `visuals/`
- Revenue, order-value, and rating breakdowns by category, region, channel, payment mode,
  age group, and weekday

## 7. Author's Note

This dataset was synthetically generated (see `generate_data.py`) to closely emulate a real
public retail sales dataset, including deliberately injected data quality issues, so that
the cleaning pipeline in the notebook solves genuine problems rather than working with
already-clean data.
