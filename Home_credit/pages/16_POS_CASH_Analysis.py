import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="POS/CASH Analysis",
    page_icon="💳",
    layout="wide"
)

load_css()

st.title("💳 POS/CASH Loan Analysis")
st.caption(
    "Analysis of point-of-sale and cash loan balances, "
    "contract status, installments, and delinquency behaviour."
)

st.divider()


# ============================================================
# BUSINESS OBJECTIVE
# ============================================================

with st.expander("🎯 Business Objective", expanded=True):
    st.markdown(
        """
        This page analyses historical **POS/CASH loan balance records**
        to understand loan status, installment behaviour and delinquency.

        The analysis focuses on:

        - Contract status
        - Installments remaining
        - Days past due (DPD)
        - Defaulted days past due
        - Monthly loan balance trends
        - Customer-level repayment indicators

        The objective is to identify descriptive repayment and delinquency
        patterns that can support the broader Home Credit EDA.

        **Important:** This is descriptive EDA only. No predictive model
        is developed.
        """
    )


# ============================================================
# LOAD POS/CASH DATA
# ============================================================

@st.cache_data
def load_pos_cash():

    possible_paths = [
        r"D:\Home_credit\data\raw\POS_CASH_balance.csv",
        r"D:\Home_credit\raw_datasets\POS_CASH_balance.csv",
        r"D:\Home_credit\POS_CASH_balance.csv"
    ]

    for path in possible_paths:

        try:
            return pd.read_csv(path)

        except FileNotFoundError:
            continue

    raise FileNotFoundError(
        "POS_CASH_balance.csv was not found. "
        "Please check the location of the file."
    )


df = load_pos_cash().copy()


# ============================================================
# NUMERIC CONVERSION
# ============================================================

numeric_columns = [
    "MONTHS_BALANCE",
    "CNT_INSTALMENT",
    "CNT_INSTALMENT_FUTURE",
    "SK_DPD",
    "SK_DPD_DEF"
]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 POS/CASH Filters")


# Contract Status
if "NAME_CONTRACT_STATUS" in df.columns:

    status_options = ["All"] + sorted(
        df["NAME_CONTRACT_STATUS"]
        .dropna()
        .unique()
        .tolist()
    )

    status_sel = st.sidebar.selectbox(
        "Contract Status",
        status_options
    )

else:

    status_sel = "All"


# DPD filter
if "SK_DPD" in df.columns:

    dpd_option = st.sidebar.selectbox(
        "Delinquency Status",
        [
            "All",
            "No DPD",
            "Has DPD"
        ]
    )

else:

    dpd_option = "All"


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df.copy()


if status_sel != "All":

    filtered = filtered[
        filtered["NAME_CONTRACT_STATUS"]
        == status_sel
    ]


if dpd_option == "No DPD":

    filtered = filtered[
        filtered["SK_DPD"].fillna(0) == 0
    ]


elif dpd_option == "Has DPD":

    filtered = filtered[
        filtered["SK_DPD"].fillna(0) > 0
    ]


# ============================================================
# EMPTY CHECK
# ============================================================

if filtered.empty:

    st.warning(
        "No POS/CASH records match the selected filters."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_records = len(filtered)

unique_customers = (
    filtered["SK_ID_CURR"]
    .nunique()
)

unique_contracts = (
    filtered["SK_ID_PREV"]
    .nunique()
)

active_contracts = (
    filtered["NAME_CONTRACT_STATUS"]
    .eq("Active")
    .sum()
)

completed_contracts = (
    filtered["NAME_CONTRACT_STATUS"]
    .eq("Completed")
    .sum()
)

avg_installments_remaining = (
    filtered["CNT_INSTALMENT_FUTURE"]
    .mean()
)

customers_with_dpd = (
    filtered.loc[
        filtered["SK_DPD"].fillna(0) > 0,
        "SK_ID_CURR"
    ]
    .nunique()
)

dpd_records = (
    filtered["SK_DPD"]
    .fillna(0)
    .gt(0)
    .sum()
)

max_dpd = (
    filtered["SK_DPD"]
    .max()
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 POS/CASH Portfolio Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card(
        "POS/CASH Records",
        f"{total_records:,}"
    )

with c2:
    kpi_card(
        "Unique Customers",
        f"{unique_customers:,}"
    )

with c3:
    kpi_card(
        "Unique Contracts",
        f"{unique_contracts:,}"
    )

with c4:
    kpi_card(
        "Active Contracts",
        f"{active_contracts:,}"
    )


c5, c6, c7, c8 = st.columns(4)

with c5:
    kpi_card(
        "Completed Contracts",
        f"{completed_contracts:,}"
    )

with c6:
    kpi_card(
        "Avg Installments Remaining",
        f"{avg_installments_remaining:.1f}"
    )

with c7:
    kpi_card(
        "Customers with DPD",
        f"{customers_with_dpd:,}"
    )

with c8:
    kpi_card(
        "Maximum DPD",
        f"{max_dpd:,.0f}"
    )


st.divider()


# ============================================================
# GRAPH 1 — CONTRACT STATUS
# ============================================================

st.subheader("1️⃣ Contract Status Distribution")

status_counts = (
    filtered["NAME_CONTRACT_STATUS"]
    .value_counts()
    .reset_index()
)

status_counts.columns = [
    "Contract Status",
    "Records"
]

fig = px.bar(
    status_counts.sort_values("Records"),
    x="Records",
    y="Contract Status",
    orientation="h",
    text="Records",
    title="POS/CASH Records by Contract Status",
    color_discrete_sequence=[
        CHART_COLORS[0]
    ]
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
# GRAPH 2 — INSTALLMENTS REMAINING
# ============================================================

st.subheader("2️⃣ Installments Remaining Distribution")

installment_data = filtered[
    "CNT_INSTALMENT_FUTURE"
].dropna()


if len(installment_data) > 0:

    fig = px.histogram(
        installment_data,
        x="CNT_INSTALMENT_FUTURE",
        nbins=40,
        title="Distribution of Future Installments",
        color_discrete_sequence=[
            CHART_COLORS[1]
        ]
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Installments Remaining",
        yaxis_title="Records"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# GRAPH 3 — DPD DISTRIBUTION
# ============================================================

st.subheader("3️⃣ Days Past Due Distribution")

dpd_data = filtered[
    "SK_DPD"
].fillna(0)


# Cap visualization at 99th percentile
# so extreme values do not dominate the chart.

dpd_cap = dpd_data.quantile(0.99)

dpd_chart = dpd_data[
    dpd_data <= dpd_cap
]


fig = px.histogram(
    dpd_chart,
    x="SK_DPD",
    nbins=40,
    title="Distribution of Days Past Due",
    color_discrete_sequence=[
        CHART_COLORS[2]
    ]
)

fig.update_layout(
    template="plotly_white",
    xaxis_title="Days Past Due",
    yaxis_title="Records"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 4 — DPD BY CONTRACT STATUS
# ============================================================

st.subheader("4️⃣ DPD by Contract Status")

box_df = filtered[
    [
        "NAME_CONTRACT_STATUS",
        "SK_DPD"
    ]
].copy()

box_df["SK_DPD"] = (
    box_df["SK_DPD"]
    .fillna(0)
)

box_cap = box_df[
    "SK_DPD"
].quantile(0.99)

box_df = box_df[
    box_df["SK_DPD"] <= box_cap
]


fig = px.box(
    box_df,
    x="NAME_CONTRACT_STATUS",
    y="SK_DPD",
    color="NAME_CONTRACT_STATUS",
    title="Days Past Due by Contract Status",
    color_discrete_sequence=CHART_COLORS
)

fig.update_layout(
    template="plotly_white",
    showlegend=False,
    xaxis_title="Contract Status",
    yaxis_title="Days Past Due"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 5 — MONTHLY BALANCE TREND
# ============================================================

st.subheader("5️⃣ Monthly POS/CASH Balance Trend")

monthly_records = (
    filtered
    .groupby("MONTHS_BALANCE")
    .size()
    .reset_index(name="Records")
    .sort_values("MONTHS_BALANCE")
)

fig = px.line(
    monthly_records,
    x="MONTHS_BALANCE",
    y="Records",
    markers=True,
    title="POS/CASH Records Across Months",
)

fig.update_layout(
    template="plotly_white",
    xaxis_title="Months Balance",
    yaxis_title="Records"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 6 — DPD EVENTS BY MONTH
# ============================================================

st.subheader("6️⃣ Monthly Delinquency Trend")

monthly_dpd = (
    filtered.assign(
        DPD_EVENT=
        filtered["SK_DPD"]
        .fillna(0)
        .gt(0)
        .astype(int)
    )
    .groupby("MONTHS_BALANCE")[
        "DPD_EVENT"
    ]
    .sum()
    .reset_index()
    .sort_values("MONTHS_BALANCE")
)

fig = px.line(
    monthly_dpd,
    x="MONTHS_BALANCE",
    y="DPD_EVENT",
    markers=True,
    title="Monthly DPD Event Trend",
    color_discrete_sequence=[
        CHART_COLORS[3]
    ]
)

fig.update_layout(
    template="plotly_white",
    xaxis_title="Months Balance",
    yaxis_title="DPD Events"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 7 — CONTRACT STATUS BY MONTH
# ============================================================

st.subheader("7️⃣ Contract Status by Month")

status_month = (
    filtered
    .groupby(
        [
            "MONTHS_BALANCE",
            "NAME_CONTRACT_STATUS"
        ]
    )
    .size()
    .reset_index(name="Records")
    .sort_values("MONTHS_BALANCE")
)

fig = px.bar(
    status_month,
    x="MONTHS_BALANCE",
    y="Records",
    color="NAME_CONTRACT_STATUS",
    title="POS/CASH Contract Status Across Months",
    barmode="stack",
    color_discrete_sequence=CHART_COLORS
)

fig.update_layout(
    template="plotly_white",
    xaxis_title="Months Balance",
    yaxis_title="Records"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 8 — INSTALLMENTS VS DPD
# ============================================================

st.subheader("8️⃣ Installments Remaining vs DPD")

scatter_df = filtered[
    [
        "CNT_INSTALMENT_FUTURE",
        "SK_DPD",
        "NAME_CONTRACT_STATUS"
    ]
].dropna()


if len(scatter_df) > 15000:

    scatter_df = scatter_df.sample(
        15000,
        random_state=42
    )


scatter_df["SK_DPD"] = (
    scatter_df["SK_DPD"]
    .clip(
        upper=scatter_df["SK_DPD"].quantile(0.99)
    )
)


fig = px.scatter(
    scatter_df,
    x="CNT_INSTALMENT_FUTURE",
    y="SK_DPD",
    color="NAME_CONTRACT_STATUS",
    opacity=0.5,
    title="Future Installments vs Days Past Due",
    labels={
        "CNT_INSTALMENT_FUTURE":
            "Installments Remaining",
        "SK_DPD":
            "Days Past Due",
        "NAME_CONTRACT_STATUS":
            "Contract Status"
    },
    color_discrete_sequence=CHART_COLORS
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# FEATURE ENGINEERING — CUSTOMER LEVEL
# ============================================================

st.divider()

st.subheader(
    "👥 Customer-Level POS/CASH Features"
)


customer_features = (
    filtered
    .groupby("SK_ID_CURR")
    .agg(
        POS_CASH_RECORD_COUNT=(
            "SK_ID_PREV",
            "count"
        ),
        POS_CASH_CONTRACT_COUNT=(
            "SK_ID_PREV",
            "nunique"
        ),
        AVERAGE_DPD=(
            "SK_DPD",
            "mean"
        ),
        MAXIMUM_DPD=(
            "SK_DPD",
            "max"
        ),
        TOTAL_DPD_EVENTS=(
            "SK_DPD",
            lambda x:
            (x.fillna(0) > 0).sum()
        ),
        AVERAGE_INSTALLMENTS_REMAINING=(
            "CNT_INSTALMENT_FUTURE",
            "mean"
        ),
        COMPLETED_CONTRACT_COUNT=(
            "NAME_CONTRACT_STATUS",
            lambda x:
            (x == "Completed").sum()
        ),
        ACTIVE_CONTRACT_COUNT=(
            "NAME_CONTRACT_STATUS",
            lambda x:
            (x == "Active").sum()
        )
    )
    .reset_index()
)


customer_features[
    "AVERAGE_DPD"
] = customer_features[
    "AVERAGE_DPD"
].fillna(0)


customer_features[
    "MAXIMUM_DPD"
] = customer_features[
    "MAXIMUM_DPD"
].fillna(0)


# ============================================================
# CUSTOMER FEATURE KPIs
# ============================================================

f1, f2, f3, f4 = st.columns(4)

with f1:

    kpi_card(
        "Customer Records",
        f"{len(customer_features):,}"
    )

with f2:

    kpi_card(
        "Avg Customer DPD",
        f"{customer_features['AVERAGE_DPD'].mean():.1f}"
    )

with f3:

    kpi_card(
        "Avg DPD Events",
        f"{customer_features['TOTAL_DPD_EVENTS'].mean():.1f}"
    )

with f4:

    kpi_card(
        "Max Customer DPD",
        f"{customer_features['MAXIMUM_DPD'].max():,.0f}"
    )


# ============================================================
# CUSTOMER DPD DISTRIBUTION
# ============================================================

st.subheader(
    "📊 Customer-Level DPD Events"
)

customer_dpd = (
    customer_features[
        "TOTAL_DPD_EVENTS"
    ]
    .value_counts()
    .sort_index()
    .head(20)
    .reset_index()
)

customer_dpd.columns = [
    "DPD Events",
    "Customers"
]

fig = px.bar(
    customer_dpd,
    x="DPD Events",
    y="Customers",
    text="Customers",
    title="Customers by Number of DPD Events",
    color_discrete_sequence=[
        CHART_COLORS[1]
    ]
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
# COMPLETED VS ACTIVE CUSTOMER CONTRACTS
# ============================================================

st.subheader(
    "📈 Active vs Completed Contracts by Customer"
)

contract_customer = pd.DataFrame({
    "Contract Type": [
        "Active",
        "Completed"
    ],
    "Contracts": [
        customer_features[
            "ACTIVE_CONTRACT_COUNT"
        ].sum(),

        customer_features[
            "COMPLETED_CONTRACT_COUNT"
        ].sum()
    ]
})


fig = px.bar(
    contract_customer,
    x="Contract Type",
    y="Contracts",
    text="Contracts",
    title="Active vs Completed POS/CASH Contracts",
    color_discrete_sequence=[
        CHART_COLORS[2]
    ]
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


most_common_status = (
    filtered[
        "NAME_CONTRACT_STATUS"
    ]
    .value_counts()
    .index[0]
)


st.markdown(
    f"""
- The filtered POS/CASH dataset contains
  **{total_records:,} monthly records**.
- There are **{unique_customers:,} unique customers** represented in the
  selected records.
- The most common contract status is **{most_common_status}**.
- The dataset contains **{unique_contracts:,} unique historical contracts**.
- The average number of future installments remaining is
  **{avg_installments_remaining:.1f}**.
- **{customers_with_dpd:,} customers** have at least one observed DPD
  record under the current filters.
- The maximum observed DPD is **{max_dpd:,.0f} days**.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown(
    """
### 1. POS/CASH history provides repayment context

Monthly POS/CASH records allow the portfolio to be analysed across the
life cycle of historical contracts.

### 2. Contract status indicates loan lifecycle

Active and completed contracts represent different stages of customer
interaction with the lending portfolio.

### 3. DPD is an important descriptive repayment indicator

Customers with observed days past due can be examined separately to
understand delinquency patterns.

### 4. Repeated DPD events deserve additional attention

A customer with several DPD events has a different observed repayment
pattern from a customer with only one isolated event.

### 5. Installments remaining provide loan lifecycle context

Customers with a large number of installments remaining may have active
longer-duration obligations.

### 6. Monthly trends can reveal changing repayment behaviour

Analysing records and DPD events across MONTHS_BALANCE helps identify
periods where delinquency activity is more concentrated.

### 7. Contract status and DPD should be considered together

A DPD observation may have a different interpretation depending on whether
the underlying contract is active or completed.

### 8. POS/CASH analysis complements installment analysis

POS/CASH data should be interpreted alongside the detailed payment-delay
analysis on Page 17.
"""
)


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.subheader("✅ Business Recommendations")

st.markdown(
    """
1. **Monitor customers with repeated DPD events** through periodic
   repayment-behaviour reviews.

2. **Create a monthly delinquency monitoring report** using POS/CASH
   balance history.

3. **Separate active and completed contracts** when analysing repayment
   patterns.

4. **Track customers with unusually high maximum DPD** for additional
   account review.

5. **Combine POS/CASH delinquency with installment payment delays** to
   identify consistent repayment stress patterns.

6. **Monitor customers with multiple active POS/CASH contracts** as part
   of portfolio exposure analysis.

7. **Use installment counts to understand loan lifecycle stage** when
   comparing customer repayment behaviour.

8. **Investigate unusual spikes in monthly DPD events** before making
   portfolio-level decisions.

9. **Combine POS/CASH indicators with bureau debt** to understand internal
   and external credit exposure.

10. **Include POS/CASH repayment indicators in descriptive EDA risk
    segmentation**, without treating them as predictive scores.

11. **Monitor customers whose DPD behaviour appears repeatedly over time**
    rather than focusing only on isolated events.

12. **Use customer-level POS/CASH aggregates in executive portfolio
    monitoring** on Page 20.
"""
)


# ============================================================
# CUSTOMER FEATURE TABLE
# ============================================================

st.divider()

with st.expander(
    "👥 View Customer-Level POS/CASH Features"
):

    st.dataframe(
        customer_features.head(1000),
        use_container_width=True
    )


# ============================================================
# FILTERED DATA TABLE
# ============================================================

with st.expander(
    "📄 View Filtered POS/CASH Records"
):

    st.dataframe(
        filtered.head(1000),
        use_container_width=True
    )


# ============================================================
# DOWNLOAD
# ============================================================

st.subheader("⬇️ Download Data")

filtered_csv = filtered.to_csv(
    index=False
)

st.download_button(
    label="Download Filtered POS/CASH Data",
    data=filtered_csv,
    file_name="filtered_pos_cash_data.csv",
    mime="text/csv"
)