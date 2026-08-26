import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Bureau Credit History",
    page_icon="🏦",
    layout="wide"
)

load_css()

st.title("🏦 Bureau Credit History Analysis")
st.caption(
    "Analysis of customers' previous credit accounts reported by "
    "other financial institutions."
)

st.divider()


# ============================================================
# BUSINESS OBJECTIVE
# ============================================================

with st.expander("🎯 Business Objective", expanded=True):
    st.markdown(
        """
        This page analyses external credit history reported in the
        **bureau.csv** dataset.

        The analysis focuses on:

        - Active and closed bureau accounts
        - Credit types
        - Credit amounts
        - Bureau debt
        - Overdue amounts
        - Historical credit duration
        - Customer-level bureau exposure

        The objective is to understand the external credit obligations
        of Home Credit customers and identify meaningful portfolio patterns.

        **Important:** These are descriptive EDA findings and should not
        be interpreted as predictions.
        """
    )


# ============================================================
# LOAD BUREAU DATA
# ============================================================

@st.cache_data
def load_bureau_data():

    possible_paths = [
        r"D:\Home_credit\data\raw\bureau.csv",
        r"D:\Home_credit\raw_datasets\bureau.csv",
        r"D:\Home_credit\bureau.csv"
    ]

    for path in possible_paths:

        try:
            bureau = pd.read_csv(path)
            return bureau

        except FileNotFoundError:
            continue

    raise FileNotFoundError(
        "bureau.csv was not found. "
        "Please check that bureau.csv is available in your project."
    )


bureau = load_bureau_data()


# ============================================================
# BASIC CLEANING
# ============================================================

bureau = bureau.copy()

numeric_columns = [
    "AMT_CREDIT_SUM",
    "AMT_CREDIT_SUM_DEBT",
    "AMT_CREDIT_SUM_OVERDUE",
    "DAYS_CREDIT",
    "DAYS_CREDIT_ENDDATE",
    "DAYS_CREDIT_UPDATE",
    "AMT_CREDIT_MAX_OVERDUE",
    "AMT_CREDIT_SUM_LIMIT",
    "AMT_CREDIT_SUM_OVERDUE"
]

for col in numeric_columns:

    if col in bureau.columns:
        bureau[col] = pd.to_numeric(
            bureau[col],
            errors="coerce"
        )


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Bureau Filters")


# Credit Active Status
if "CREDIT_ACTIVE" in bureau.columns:

    active_options = ["All"] + sorted(
        bureau["CREDIT_ACTIVE"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    active_sel = st.sidebar.selectbox(
        "Credit Status",
        active_options
    )

else:
    active_sel = "All"


# Credit Type
if "CREDIT_TYPE" in bureau.columns:

    credit_type_options = ["All"] + sorted(
        bureau["CREDIT_TYPE"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    credit_type_sel = st.sidebar.selectbox(
        "Credit Type",
        credit_type_options
    )

else:
    credit_type_sel = "All"


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = bureau.copy()

if active_sel != "All":

    filtered = filtered[
        filtered["CREDIT_ACTIVE"] == active_sel
    ]

if credit_type_sel != "All":

    filtered = filtered[
        filtered["CREDIT_TYPE"] == credit_type_sel
    ]


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered.empty:

    st.warning(
        "No bureau records match the selected filters."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

bureau_accounts = len(filtered)

unique_customers = (
    filtered["SK_ID_CURR"].nunique()
    if "SK_ID_CURR" in filtered.columns
    else 0
)

active_credits = (
    (filtered["CREDIT_ACTIVE"] == "Active").sum()
    if "CREDIT_ACTIVE" in filtered.columns
    else 0
)

closed_credits = (
    (filtered["CREDIT_ACTIVE"] == "Closed").sum()
    if "CREDIT_ACTIVE" in filtered.columns
    else 0
)

total_bureau_debt = (
    filtered["AMT_CREDIT_SUM_DEBT"].sum()
    if "AMT_CREDIT_SUM_DEBT" in filtered.columns
    else 0
)

total_overdue = (
    filtered["AMT_CREDIT_SUM_OVERDUE"].sum()
    if "AMT_CREDIT_SUM_OVERDUE" in filtered.columns
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Bureau Portfolio Snapshot")

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card(
        "Bureau Accounts",
        f"{bureau_accounts:,}"
    )

with c2:
    kpi_card(
        "Customers with Bureau History",
        f"{unique_customers:,}"
    )

with c3:
    kpi_card(
        "Active Credits",
        f"{active_credits:,}"
    )

with c4:
    kpi_card(
        "Closed Credits",
        f"{closed_credits:,}"
    )


c5, c6, c7, c8 = st.columns(4)

with c5:
    kpi_card(
        "Total Bureau Debt",
        f"₹{total_bureau_debt:,.0f}"
    )

with c6:
    kpi_card(
        "Total Overdue Amount",
        f"₹{total_overdue:,.0f}"
    )

with c7:

    avg_credit = filtered[
        "AMT_CREDIT_SUM"
    ].mean()

    kpi_card(
        "Average Bureau Credit",
        f"₹{avg_credit:,.0f}"
    )

with c8:

    max_overdue = filtered[
        "AMT_CREDIT_SUM_OVERDUE"
    ].max()

    kpi_card(
        "Maximum Overdue",
        f"₹{max_overdue:,.0f}"
    )


st.divider()


# ============================================================
# GRAPH 1 — ACTIVE VS CLOSED
# ============================================================

st.subheader("1️⃣ Active vs Closed Bureau Loans")

status_counts = (
    filtered["CREDIT_ACTIVE"]
    .value_counts()
    .reset_index()
)

status_counts.columns = [
    "Credit Status",
    "Accounts"
]

fig = px.bar(
    status_counts,
    x="Credit Status",
    y="Accounts",
    text="Accounts",
    title="Bureau Accounts by Current Status",
    color_discrete_sequence=[CHART_COLORS[0]]
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 2 — CREDIT TYPE DISTRIBUTION
# ============================================================

st.subheader("2️⃣ Credit Type Distribution")

credit_type_counts = (
    filtered["CREDIT_TYPE"]
    .value_counts()
    .head(15)
    .sort_values()
    .reset_index()
)

credit_type_counts.columns = [
    "Credit Type",
    "Accounts"
]

fig = px.bar(
    credit_type_counts,
    x="Accounts",
    y="Credit Type",
    orientation="h",
    text="Accounts",
    title="Top Bureau Credit Types",
    color_discrete_sequence=[CHART_COLORS[1]]
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    showlegend=False,
    height=600
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 3 — CREDIT AMOUNT DISTRIBUTION
# ============================================================

st.subheader("3️⃣ Bureau Credit Amount Distribution")

credit_values = (
    filtered["AMT_CREDIT_SUM"]
    .replace([np.inf, -np.inf], np.nan)
    .dropna()
)

# Remove negative/invalid values for distribution
credit_values = credit_values[
    credit_values >= 0
]

fig = px.histogram(
    credit_values,
    x="AMT_CREDIT_SUM",
    nbins=50,
    title="Distribution of Bureau Credit Amount",
    labels={
        "AMT_CREDIT_SUM": "Bureau Credit Amount"
    },
    color_discrete_sequence=[CHART_COLORS[2]]
)

fig.update_layout(
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 4 — BUREAU DEBT DISTRIBUTION
# ============================================================

st.subheader("4️⃣ Bureau Debt Distribution")

debt_values = (
    filtered["AMT_CREDIT_SUM_DEBT"]
    .replace([np.inf, -np.inf], np.nan)
    .dropna()
)

debt_values = debt_values[
    debt_values >= 0
]

fig = px.histogram(
    debt_values,
    x="AMT_CREDIT_SUM_DEBT",
    nbins=50,
    title="Distribution of Bureau Outstanding Debt",
    labels={
        "AMT_CREDIT_SUM_DEBT": "Bureau Debt"
    },
    color_discrete_sequence=[CHART_COLORS[3]]
)

fig.update_layout(
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 5 — OVERDUE DISTRIBUTION
# ============================================================

st.subheader("5️⃣ Overdue Amount Distribution")

overdue_values = (
    filtered["AMT_CREDIT_SUM_OVERDUE"]
    .replace([np.inf, -np.inf], np.nan)
    .dropna()
)

overdue_values = overdue_values[
    overdue_values >= 0
]

fig = px.histogram(
    overdue_values,
    x="AMT_CREDIT_SUM_OVERDUE",
    nbins=40,
    title="Distribution of Bureau Overdue Amount",
    labels={
        "AMT_CREDIT_SUM_OVERDUE": "Overdue Amount"
    },
    color_discrete_sequence=[CHART_COLORS[0]]
)

fig.update_layout(
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 6 — CREDIT TYPE VS TOTAL DEBT
# ============================================================

st.subheader("6️⃣ Credit Type vs Total Bureau Debt")

debt_by_type = (
    filtered.groupby("CREDIT_TYPE")
    .agg(
        Total_Debt=(
            "AMT_CREDIT_SUM_DEBT",
            "sum"
        ),
        Accounts=(
            "SK_ID_BUREAU",
            "count"
        )
    )
    .reset_index()
)

debt_by_type = debt_by_type.sort_values(
    "Total_Debt",
    ascending=False
).head(15)

fig = px.bar(
    debt_by_type.sort_values(
        "Total_Debt"
    ),
    x="Total_Debt",
    y="CREDIT_TYPE",
    orientation="h",
    text="Total_Debt",
    title="Total Bureau Debt by Credit Type",
    labels={
        "CREDIT_TYPE": "Credit Type",
        "Total_Debt": "Total Bureau Debt"
    },
    color_discrete_sequence=[CHART_COLORS[1]]
)

fig.update_traces(
    texttemplate="₹%{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    showlegend=False,
    height=600
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 7 — BUREAU CREDIT VS DEBT
# ============================================================

st.subheader("7️⃣ Bureau Credit vs Outstanding Debt")

scatter_df = filtered[
    [
        "AMT_CREDIT_SUM",
        "AMT_CREDIT_SUM_DEBT",
        "CREDIT_ACTIVE",
        "CREDIT_TYPE"
    ]
].dropna()

# Limit points for browser performance
if len(scatter_df) > 15000:

    scatter_df = scatter_df.sample(
        15000,
        random_state=42
    )

fig = px.scatter(
    scatter_df,
    x="AMT_CREDIT_SUM",
    y="AMT_CREDIT_SUM_DEBT",
    color="CREDIT_ACTIVE",
    hover_data=[
        "CREDIT_TYPE"
    ],
    title="Bureau Credit Amount vs Outstanding Debt",
    labels={
        "AMT_CREDIT_SUM": "Credit Amount",
        "AMT_CREDIT_SUM_DEBT": "Outstanding Debt",
        "CREDIT_ACTIVE": "Credit Status"
    },
    opacity=0.55
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 8 — CREDIT HISTORY BY AGE OF ACCOUNT
# ============================================================

st.subheader("8️⃣ Credit History Duration")

days_credit = (
    filtered["DAYS_CREDIT"]
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
    .dropna()
)

# DAYS_CREDIT is negative because it represents
# time before the current application.

history_years = (
    days_credit.abs() / 365
)

fig = px.histogram(
    history_years,
    x=history_years,
    nbins=40,
    title="Distribution of Bureau Credit History Age",
    labels={
        "x": "Years Since Bureau Credit Was Reported"
    },
    color_discrete_sequence=[CHART_COLORS[2]]
)

fig.update_layout(
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CUSTOMER-LEVEL BUREAU FEATURES
# ============================================================

st.divider()

st.subheader("👥 Customer-Level Bureau Features")

customer_bureau = (
    filtered.groupby("SK_ID_CURR")
    .agg(
        BUREAU_ACCOUNT_COUNT=(
            "SK_ID_BUREAU",
            "nunique"
        ),
        ACTIVE_BUREAU_COUNT=(
            "CREDIT_ACTIVE",
            lambda x: (x == "Active").sum()
        ),
        CLOSED_BUREAU_COUNT=(
            "CREDIT_ACTIVE",
            lambda x: (x == "Closed").sum()
        ),
        TOTAL_BUREAU_CREDIT=(
            "AMT_CREDIT_SUM",
            "sum"
        ),
        TOTAL_BUREAU_DEBT=(
            "AMT_CREDIT_SUM_DEBT",
            "sum"
        ),
        AVERAGE_BUREAU_CREDIT=(
            "AMT_CREDIT_SUM",
            "mean"
        ),
        MAX_OVERDUE_AMOUNT=(
            "AMT_CREDIT_SUM_OVERDUE",
            "max"
        ),
        TOTAL_OVERDUE_AMOUNT=(
            "AMT_CREDIT_SUM_OVERDUE",
            "sum"
        )
    )
    .reset_index()
)


# ============================================================
# CUSTOMER KPI
# ============================================================

cc1, cc2, cc3, cc4 = st.columns(4)

with cc1:

    kpi_card(
        "Customers Analysed",
        f"{len(customer_bureau):,}"
    )

with cc2:

    kpi_card(
        "Avg Accounts / Customer",
        f"{customer_bureau['BUREAU_ACCOUNT_COUNT'].mean():.1f}"
    )

with cc3:

    customers_with_debt = (
        customer_bureau["TOTAL_BUREAU_DEBT"] > 0
    ).sum()

    kpi_card(
        "Customers with Bureau Debt",
        f"{customers_with_debt:,}"
    )

with cc4:

    customers_overdue = (
        customer_bureau["MAX_OVERDUE_AMOUNT"] > 0
    ).sum()

    kpi_card(
        "Customers with Overdue",
        f"{customers_overdue:,}"
    )


# ============================================================
# CUSTOMER-LEVEL TABLE
# ============================================================

st.dataframe(
    customer_bureau.head(1000),
    use_container_width=True
)


# ============================================================
# CUSTOMER BUREAU ACCOUNT DISTRIBUTION
# ============================================================

st.subheader("📊 Bureau Accounts per Customer")

account_distribution = (
    customer_bureau["BUREAU_ACCOUNT_COUNT"]
    .value_counts()
    .sort_index()
    .reset_index()
)

account_distribution.columns = [
    "Bureau Accounts",
    "Customers"
]

account_distribution = account_distribution.head(15)

fig = px.bar(
    account_distribution,
    x="Bureau Accounts",
    y="Customers",
    text="Customers",
    title="Number of Bureau Accounts per Customer",
    color_discrete_sequence=[CHART_COLORS[3]]
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# KEY OBSERVATIONS
# ============================================================

st.divider()

st.subheader("🔍 Key Observations")

top_credit_type = (
    filtered["CREDIT_TYPE"]
    .value_counts()
    .index[0]
)

top_credit_type_count = (
    filtered["CREDIT_TYPE"]
    .value_counts()
    .iloc[0]
)

top_status = (
    filtered["CREDIT_ACTIVE"]
    .value_counts()
    .index[0]
)

highest_debt_type = debt_by_type.iloc[0]["CREDIT_TYPE"]

st.markdown(
    f"""
- The filtered bureau dataset contains **{bureau_accounts:,} bureau
  account records across **{unique_customers:,} customers**.
- **{top_status}** is the most common bureau account status.
- **{top_credit_type}** is the most frequently reported credit type,
  with **{top_credit_type_count:,} accounts**.
- Total outstanding bureau debt in the filtered portfolio is
  approximately **₹{total_bureau_debt:,.0f}**.
- Total recorded overdue amount is approximately
  **₹{total_overdue:,.0f}**.
- **{highest_debt_type}** contributes the largest total bureau debt
  among the displayed credit types.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown(
    """
### 1. External credit history provides additional portfolio context

Bureau records reveal customers' credit obligations outside their current
Home Credit application.

### 2. Active and closed accounts should be analysed separately

An active external credit account represents a different current exposure
from a closed historical account.

### 3. Bureau debt is different from total bureau credit

Credit amount represents the reported credit exposure, while bureau debt
provides information about outstanding obligations.

### 4. Overdue amounts identify a specific repayment concern

Customers with recorded overdue bureau balances can be investigated further
alongside their current application and repayment behaviour.

### 5. Credit type concentration matters

A small number of credit types may account for a substantial proportion of
bureau exposure. These categories should therefore be monitored separately.

### 6. Customer-level aggregation is important

Account-level records can make customers with many accounts appear more
prominent. Aggregating bureau information at customer level provides a
clearer portfolio view.
"""
)


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.subheader("✅ Business Recommendations")

st.markdown(
    """
1. **Monitor customers with multiple active bureau accounts** as part of
   external credit exposure analysis.

2. **Track total bureau debt at customer level** rather than relying only
   on individual account records.

3. **Flag customers with recorded overdue bureau balances** for additional
   review.

4. **Compare bureau debt with current Home Credit credit exposure** to
   understand total observed credit obligations.

5. **Monitor credit-type concentration** when reviewing external portfolio
   exposure.

6. **Separate active and closed bureau accounts** in management reporting.

7. **Combine bureau debt with affordability ratios** from Page 10 for a
   more complete view of financial burden.

8. **Combine bureau history with installment behaviour** from Page 17 to
   investigate whether external obligations coincide with payment delays.

9. **Create customer-level bureau aggregates** for consistent portfolio
   monitoring.

10. **Investigate extreme overdue values individually** before assuming
    they represent systematic customer risk.
"""
)


# ============================================================
# DOWNLOAD CUSTOMER-LEVEL FEATURES
# ============================================================

st.divider()

st.subheader("⬇️ Download Bureau Analysis Data")

bureau_csv = customer_bureau.to_csv(
    index=False
)

st.download_button(
    label="Download Customer-Level Bureau Features",
    data=bureau_csv,
    file_name="customer_bureau_features.csv",
    mime="text/csv"
)


# ============================================================
# RAW FILTERED DATA
# ============================================================

with st.expander("📄 View Filtered Bureau Records"):

    st.dataframe(
        filtered.head(1000),
        use_container_width=True
    )

    filtered_csv = filtered.to_csv(
        index=False
    )

    st.download_button(
        label="Download Filtered Bureau Records",
        data=filtered_csv,
        file_name="filtered_bureau_records.csv",
        mime="text/csv"
    )