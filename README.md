# 📦 Delivery Delay Root Cause & Cost Analysis

An end-to-end Data Analytics project that analyzes e-commerce delivery data using **SQL, Python, Excel, and Power BI**. The project focuses on identifying why orders are delivered late, calculating the cost impact, predicting which future orders are at risk, and building an interactive Power BI dashboard to help operations teams prioritize fixes.

---

## 🎯 Business Problem

An e-commerce company promises customers a delivery date, but a meaningful share of orders arrive late. Every late order triggers a refund/compensation cost, and repeated delays risk losing repeat customers. The operations team knew delays were happening but had no clear view of:

- How big the problem actually is, and whether it's getting worse
- Which hub, courier partner, or order type is driving most of the delays
- What it's actually costing the business
- Which orders to prioritize checking first

This project answers all four questions — moving from raw data → root-cause analysis → cost impact → risk prediction → an actionable dashboard.

---

## 📌 Project Objectives

- Clean and organize raw delivery order data.
- Perform exploratory data analysis (EDA) using Python.
- Analyze delay patterns using SQL queries (simple + advanced).
- Build a cost-impact calculator in Excel.
- Predict which orders are at risk of being late using a simple ML model.
- Build an interactive Power BI dashboard.
- Extract meaningful business insights to support decision-making.

---

## 🛠️ Tech Stack

- **Python**
  - Pandas
  - Matplotlib
  - Scikit-learn

- **Database**
  - MySQL

- **Spreadsheet**
  - Excel (formulas, cost modeling)

- **Visualization**
  - Power BI

- **IDE**
  - VS Code

---

## 📂 Project Structure

```
Delivery-Delay-Analysis/
│
├── data/
│   └── raw_orders_dataset.csv
│
├── sql/
│   └── fulfillment_queries.sql
│
├── python/
│   ├── eda_model_script.py
│   └── orders_with_risk_score.csv
│
├── excel/
│   └── hub_cost_tracker.xlsx
│
├── power BI/
│   └── delivery delay analysis.pbix
│
├── Delivery delay analysis.pdf
└── README.md
```

---

## 🧹 Data Preparation

The dataset was checked and prepared using Python by performing:

- Handling missing values in critical fields (hub, courier, distance)
- Checking data types and converting date columns
- Creating a distance-band feature for analysis
- Calculating delay days (actual vs. promised delivery date)

---

## 📈 Exploratory Data Analysis (EDA)

The following analyses were performed using Python:

- Late Delivery % by Hub
- Late Delivery % by Courier Partner
- Late Delivery % by Distance Band
- Late Delivery % Trend by Month

---

## 🗄️ SQL Analysis

Business insights were generated using MySQL with queries such as:

- Overall Late Delivery %
- Late % by Hub
- Late % by Courier Partner
- Late % on Weekends vs. Weekdays
- Worst Hub + Courier Combinations (CTE + Window Functions)
- Month-over-Month Delay Trend with Rolling Average
- Late % by Distance Band

A total of **7 SQL queries** were used for analysis, split across simple aggregations and more advanced window-function queries.

---

## 🤖 Prediction Model (Python)

A simple Logistic Regression model was built to predict whether an order will be late:

- Time-based train/test split (trained on older orders, tested on newer orders)
- Evaluated using precision, recall, F1-score, ROC-AUC, and a confusion matrix
- Business metric: checking the **top 10% highest-risk orders catches ~18% of all late orders**
- Final model retrained on full historical data to generate a risk score for every order

---

## 💰 Cost Impact (Excel)

- Direct compensation cost calculated per hub using SUMIFS/COUNTIFS formulas
- Kept clearly separate from an illustrative "revenue at risk" scenario, which is explicitly labeled as an assumption, not a measured cost
- Priority list of the top 100 highest-risk orders for the operations team

---

# 📊 Power BI Dashboard

The dashboard consists of **3 interactive pages**.

## 📄 Page 1 – Overview

Features:

- Total Orders
- Late Orders
- Late Delivery %
- Total Direct Cost
- Late Delivery % Trend (Jan–Dec 2024)

---

## 📄 Page 2 – Root Causes

Features:

- Late Delivery % by Hub
- Late Delivery % by Courier Partner
- Late Delivery % by Distance Band

---

## 📄 Page 3 – Action Plan

Features:

- Cost Impact by Hub (Ranked, with Total row)
- Top 100 Highest-Risk Orders — Ops Action List
- Key insight callouts summarizing where to focus first

---

## 📊 Key Business Insights

- Overall late delivery rate is **26.5%** across 12,000 orders.
- **Hub_D_Kolkata** is the biggest problem hub — **45.6%** late, nearly double every other hub.
- **SwiftGo** is the weakest courier partner — **42.1%** late, 17+ points worse than the next courier.
- The **Hub_D_Kolkata + SwiftGo** combination is the worst pairing at **62.9%** late.
- Orders **over 400km** are ~13 points more likely to be late than shorter-distance orders.
- **October** shows a clear seasonal spike (31.9% late), consistent with festive-season order volume.
- Direct compensation cost totals **₹4,76,400**, with **Hub_D_Kolkata alone accounting for ~32%** of that.
- Checking just the **top 10% highest-risk orders catches ~18%** of all late orders — a far more efficient use of ops time than checking orders at random.

---

## 📚 Skills Demonstrated

- Data Cleaning & Preparation
- Exploratory Data Analysis
- SQL (Aggregations, CTEs, Window Functions)
- Predictive Modeling (Logistic Regression)
- Model Evaluation (Precision, Recall, F1, ROC-AUC)
- Excel Financial Modeling
- Power BI Dashboard Design
- Business Analytics & Data Storytelling

---

## 👨‍💻 Author

**Sarthak Mandal**
