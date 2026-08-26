import streamlit as st
import pandas as pd
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Loan Application Analysis",
    page_icon="💳",
    layout="wide"
)

load_css()

st.title("💳 Current Loan Application Analysis")
st.caption(
    "Explore current Home Credit applications, loan amounts, "
    "annuity patterns, product pricing, and application timing."
)

st.divider()


# ============================================================
# BUSINESS OBJECTIVE
# ============================================================

with st.expander("🎯 Business Objective", expanded=True):
    st.markdown(
        """
        This page analyses the structure and characteristics of current
        Home Credit loan applications.

        The analysis focuses on:

        - Contract type
        - Credit amount
        - Annuity amount
        - Goods price
        - Application weekday
        - Application hour
        - Credit-to-goods relationship
        - Application patterns across customer segments

        The objective is to understand the typical loan application,
        identify common credit ranges, and discover unusual application
        patterns.

        **This page is descriptive EDA only. No predictive model is used.**
        """
    )


# ============================================================
# LOAD DATA
# ============================================================

df = load_data()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Filters")


# Contract Type
contract_options = ["All"] + sorted(
    df["NAME_CONTRACT_TYPE"].dropna().unique().tolist()
)

contract_sel = st.sidebar.selectbox(
    "Contract Type",
    contract_options
)


# Gender
gender_options = ["All"] + sorted(
    df["CODE_GENDER"].dropna().unique().tolist()
)

gender_sel = st.sidebar.selectbox(
    "Gender",
    gender_options
)


# Age Group
age_options = ["All"] + sorted(
    df["AGE_GROUP"].dropna().unique().tolist()
)

age_sel = st.sidebar.selectbox(
    "Age Group",
    age_options
)


# Income Group
income_options = ["All"] + sorted(
    df["INCOME_GROUP"].dropna().unique().tolist()
)

income_sel = st.sidebar.selectbox(
    "Income Group",
    income_options
)


# Education
education_options = ["All"] + sorted(
    df["NAME_EDUCATION_TYPE"].dropna().unique().tolist()
)

education_sel = st.sidebar.selectbox(
    "Education",
    education_options
)


# Employment Group
employment_options = ["All"] + sorted(
    df["EMPLOYMENT_GROUP"].dropna().unique().tolist()
)

employment_sel = st.sidebar.selectbox(
    "Employment Group",
    employment_options
)


# Default Status
default_options = [
    "All",
    "Non-Default",
    "Default"
]

default_sel = st.sidebar.selectbox(
    "Default Status",
    default_options
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df.copy()


if contract_sel != "All":
    filtered = filtered[
        filtered["NAME_CONTRACT_TYPE"] == contract_sel
    ]


if gender_sel != "All":
    filtered = filtered[
        filtered["CODE_GENDER"] == gender_sel
    ]


if age_sel != "All":
    filtered = filtered[
        filtered["AGE_GROUP"] == age_sel
    ]


if income_sel != "All":
    filtered = filtered[
        filtered["INCOME_GROUP"] == income_sel
    ]


if education_sel != "All":
    filtered = filtered[
        filtered["NAME_EDUCATION_TYPE"] == education_sel
    ]


if employment_sel != "All":
    filtered = filtered[
        filtered["EMPLOYMENT_GROUP"] == employment_sel
    ]


if default_sel == "Default":
    filtered = filtered[
        filtered["TARGET"] == 1
    ]

elif default_sel == "Non-Default":
    filtered = filtered[
        filtered["TARGET"] == 0
    ]


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered.empty:
    st.warning(
        "No applications match the selected filters. "
        "Please adjust the filters."
    )
    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_applications = len(filtered)

average_credit = filtered["AMT_CREDIT"].mean()

median_credit = filtered["AMT_CREDIT"].median()

average_annuity = filtered["AMT_ANNUITY"].mean()

average_goods_price = filtered["AMT_GOODS_PRICE"].mean()

contract_mode = (
    filtered["NAME_CONTRACT_TYPE"]
    .dropna()
    .mode()
)

most_common_contract = (
    contract_mode.iloc[0]
    if not contract_mode.empty
    else "N/A"
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Loan Application Snapshot")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    kpi_card(
        "Total Applications",
        f"{total_applications:,}"
    )

with c2:
    kpi_card(
        "Average Credit",
        f"₹{average_credit:,.0f}"
    )

with c3:
    kpi_card(
        "Median Credit",
        f"₹{median_credit:,.0f}"
    )

with c4:
    kpi_card(
        "Average Annuity",
        f"₹{average_annuity:,.0f}"
    )

with c5:
    kpi_card(
        "Most Common Contract",
        str(most_common_contract)
    )


st.divider()


# ============================================================
# APPLICATIONS BY CONTRACT TYPE
# ============================================================

st.subheader("📑 Applications by Contract Type")

contract_counts = (
    filtered["NAME_CONTRACT_TYPE"]
    .value_counts()
    .reset_index()
)

contract_counts.columns = [
    "Contract Type",
    "Applications"
]

fig = px.bar(
    contract_counts,
    x="Contract Type",
    y="Applications",
    title="Applications by Contract Type",
    text="Applications",
    color_discrete_sequence=[
        CHART_COLORS[0]
    ]
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CREDIT AMOUNT DISTRIBUTION
# ============================================================

st.subheader("💰 Credit Amount Distribution")

credit_limit = filtered[
    "AMT_CREDIT"
].quantile(0.99)

credit_chart = filtered[
    filtered["AMT_CREDIT"] <= credit_limit
]

fig = px.histogram(
    credit_chart,
    x="AMT_CREDIT",
    nbins=50,
    title="Credit Amount Distribution — Up to 99th Percentile",
    labels={
        "AMT_CREDIT": "Credit Amount"
    },
    color_discrete_sequence=[
        CHART_COLORS[1]
    ]
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# ANNUITY DISTRIBUTION
# ============================================================

st.subheader("💵 Annuity Distribution")

annuity_limit = filtered[
    "AMT_ANNUITY"
].quantile(0.99)

annuity_chart = filtered[
    filtered["AMT_ANNUITY"] <= annuity_limit
]

fig = px.histogram(
    annuity_chart,
    x="AMT_ANNUITY",
    nbins=50,
    title="Annuity Distribution — Up to 99th Percentile",
    labels={
        "AMT_ANNUITY": "Annuity Amount"
    },
    color_discrete_sequence=[
        CHART_COLORS[2]
    ]
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GOODS PRICE DISTRIBUTION
# ============================================================

st.subheader("🏷️ Goods Price Distribution")

goods_limit = filtered[
    "AMT_GOODS_PRICE"
].quantile(0.99)

goods_chart = filtered[
    filtered["AMT_GOODS_PRICE"] <= goods_limit
]

fig = px.histogram(
    goods_chart,
    x="AMT_GOODS_PRICE",
    nbins=50,
    title="Goods Price Distribution — Up to 99th Percentile",
    labels={
        "AMT_GOODS_PRICE": "Goods Price"
    },
    color_discrete_sequence=[
        CHART_COLORS[3]
    ]
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CREDIT VS GOODS PRICE
# ============================================================

st.subheader("💳 Credit Amount vs Goods Price")

credit_goods = filtered[
    [
        "AMT_CREDIT",
        "AMT_GOODS_PRICE",
        "TARGET",
        "NAME_CONTRACT_TYPE"
    ]
].dropna()

# Limit extreme values only for visualization
credit_goods = credit_goods[
    credit_goods["AMT_CREDIT"] <=
    credit_goods["AMT_CREDIT"].quantile(0.99)
]

credit_goods = credit_goods[
    credit_goods["AMT_GOODS_PRICE"] <=
    credit_goods["AMT_GOODS_PRICE"].quantile(0.99)
]

fig = px.scatter(
    credit_goods,
    x="AMT_GOODS_PRICE",
    y="AMT_CREDIT",
    title="Credit Amount vs Goods Price",
    labels={
        "AMT_GOODS_PRICE": "Goods Price",
        "AMT_CREDIT": "Credit Amount"
    },
    color="NAME_CONTRACT_TYPE",
    opacity=0.55
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CREDIT VS ANNUITY
# ============================================================

st.subheader("💰 Credit Amount vs Annuity")

credit_annuity = filtered[
    [
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "TARGET"
    ]
].dropna()

credit_annuity = credit_annuity[
    credit_annuity["AMT_CREDIT"] <=
    credit_annuity["AMT_CREDIT"].quantile(0.99)
]

credit_annuity = credit_annuity[
    credit_annuity["AMT_ANNUITY"] <=
    credit_annuity["AMT_ANNUITY"].quantile(0.99)
]

fig = px.scatter(
    credit_annuity,
    x="AMT_CREDIT",
    y="AMT_ANNUITY",
    title="Credit Amount vs Annuity",
    labels={
        "AMT_CREDIT": "Credit Amount",
        "AMT_ANNUITY": "Annuity Amount"
    },
    opacity=0.55
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# APPLICATIONS BY WEEKDAY
# ============================================================

st.subheader("📅 Applications by Weekday")

weekday_order = [
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
    "SUNDAY"
]

weekday_counts = (
    filtered["WEEKDAY_APPR_PROCESS_START"]
    .value_counts()
    .reindex(weekday_order)
    .fillna(0)
    .reset_index()
)

weekday_counts.columns = [
    "Weekday",
    "Applications"
]

fig = px.bar(
    weekday_counts,
    x="Weekday",
    y="Applications",
    title="Applications by Weekday",
    text="Applications",
    color_discrete_sequence=[
        CHART_COLORS[0]
    ]
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# APPLICATIONS BY HOUR
# ============================================================

st.subheader("⏰ Applications by Hour")

hour_counts = (
    filtered["HOUR_APPR_PROCESS_START"]
    .value_counts()
    .sort_index()
    .reset_index()
)

hour_counts.columns = [
    "Hour",
    "Applications"
]

fig = px.line(
    hour_counts,
    x="Hour",
    y="Applications",
    markers=True,
    title="Applications by Hour of Day",
    labels={
        "Hour": "Application Hour",
        "Applications": "Number of Applications"
    }
)

fig.update_layout(
    template="plotly_white",
    xaxis=dict(
        dtick=1
    ),
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CREDIT DISTRIBUTION BY INCOME GROUP
# ============================================================

st.subheader("💵 Credit Amount by Income Group")

income_credit = filtered[
    [
        "INCOME_GROUP",
        "AMT_CREDIT"
    ]
].dropna()

credit_income_limit = income_credit[
    "AMT_CREDIT"
].quantile(0.99)

income_credit = income_credit[
    income_credit["AMT_CREDIT"] <= credit_income_limit
]

fig = px.box(
    income_credit,
    x="INCOME_GROUP",
    y="AMT_CREDIT",
    title="Credit Amount Distribution by Income Group",
    labels={
        "INCOME_GROUP": "Income Group",
        "AMT_CREDIT": "Credit Amount"
    }
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CONTRACT TYPE VS DEFAULT RATE
# ============================================================

st.subheader("⚠️ Contract Type vs Observed Default Rate")

contract_risk = (
    filtered.groupby(
        "NAME_CONTRACT_TYPE"
    )
    .agg(
        Applications=("TARGET", "size"),
        Defaults=("TARGET", "sum"),
        Default_Rate=("TARGET", "mean")
    )
    .reset_index()
)

contract_risk["Default_Rate"] *= 100

fig = px.bar(
    contract_risk,
    x="NAME_CONTRACT_TYPE",
    y="Default_Rate",
    title="Observed Default Rate by Contract Type",
    text="Default_Rate",
    labels={
        "NAME_CONTRACT_TYPE": "Contract Type",
        "Default_Rate": "Observed Default Rate (%)"
    },
    color_discrete_sequence=[
        CHART_COLORS[2]
    ]
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# SUMMARY TABLE
# ============================================================

st.divider()

st.subheader("📋 Loan Application Summary")

summary = (
    filtered.groupby(
        "NAME_CONTRACT_TYPE"
    )
    .agg(
        Applications=("SK_ID_CURR", "count"),
        Average_Credit=("AMT_CREDIT", "mean"),
        Median_Credit=("AMT_CREDIT", "median"),
        Average_Annuity=("AMT_ANNUITY", "mean"),
        Average_Goods_Price=("AMT_GOODS_PRICE", "mean"),
        Average_Income=("AMT_INCOME_TOTAL", "mean"),
        Defaults=("TARGET", "sum"),
        Default_Rate=("TARGET", "mean")
    )
    .reset_index()
)

summary["Default_Rate"] *= 100

st.dataframe(
    summary.style.format(
        {
            "Applications": "{:,.0f}",
            "Average_Credit": "₹{:,.0f}",
            "Median_Credit": "₹{:,.0f}",
            "Average_Annuity": "₹{:,.0f}",
            "Average_Goods_Price": "₹{:,.0f}",
            "Average_Income": "₹{:,.0f}",
            "Defaults": "{:,.0f}",
            "Default_Rate": "{:.2f}%"
        }
    ),
    use_container_width=True
)


# ============================================================
# KEY OBSERVATIONS
# ============================================================

st.subheader("🔍 Key Observations")

credit_median = filtered["AMT_CREDIT"].median()

highest_credit_income = (
    filtered.groupby("INCOME_GROUP")["AMT_CREDIT"]
    .mean()
    .idxmax()
)

highest_credit_income_value = (
    filtered.groupby("INCOME_GROUP")["AMT_CREDIT"]
    .mean()
    .max()
)


peak_weekday = (
    weekday_counts.loc[
        weekday_counts["Applications"].idxmax(),
        "Weekday"
    ]
)

peak_hour = (
    hour_counts.loc[
        hour_counts["Applications"].idxmax(),
        "Hour"
    ]
)

st.markdown(
    f"""
- The filtered portfolio contains **{total_applications:,} current loan
  applications**.
- The median requested credit amount is approximately
  **₹{credit_median:,.0f}**, giving a better view of the typical application
  than the mean alone.
- The most common contract type is **{most_common_contract}**.
- The income group with the highest average credit amount is
  **{highest_credit_income}**, with an average credit of approximately
  **₹{highest_credit_income_value:,.0f}**.
- **{peak_weekday}** has the highest number of applications in the filtered
  portfolio.
- The peak application hour is approximately **{peak_hour}:00**.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown(
    """
### 1. Credit distribution should be evaluated using both mean and median

Loan amounts can contain extreme values. Comparing the mean and median
provides a clearer picture of the typical customer application.

### 2. Credit and goods price are closely related application dimensions

Comparing requested credit with the underlying goods price helps identify
applications where the financing amount differs substantially from the
reported goods value.

### 3. Annuity provides an additional view of loan burden

Customers applying for larger credit amounts may also have higher scheduled
annuity payments. This relationship should be explored further on the
Credit Affordability page.

### 4. Application timing can reveal operational patterns

Weekday and hourly application distributions can help identify when most
applications enter the lending process.

### 5. Income groups can have different credit exposure

Comparing credit distributions across income groups helps identify which
segments are receiving larger loan amounts.

### 6. Contract type should be monitored separately

Different contract types may represent different lending products and can
therefore have different application volumes and observed default rates.

### 7. Default rate and default count should not be confused

A large application segment can naturally contain more defaults simply because
it contains more customers. Rates should therefore be evaluated alongside
application volume.
"""
)


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader("✅ Business Recommendations")

st.markdown(
    """
1. **Monitor the distribution of credit amounts** rather than relying only
   on average credit.

2. **Compare credit against goods price** to identify unusual financing
   patterns.

3. **Use median credit as a portfolio monitoring metric** because extreme
   loan values can distort the mean.

4. **Track annuity alongside credit amount** when assessing potential
   affordability pressure.

5. **Monitor credit exposure by income group** to identify segments carrying
   larger loan amounts.

6. **Track application volumes by weekday and hour** to understand operational
   demand patterns.

7. **Investigate unusual application patterns** rather than automatically
   treating them as problematic.

8. **Compare contract types using both volume and observed default rate** so
   that small segments are not overinterpreted.

9. **Use this page together with Page 10 — Credit Affordability Analysis**
   for a more complete assessment of loan burden.
"""
)


# ============================================================
# DETAILED FILTERED DATA
# ============================================================

st.divider()

with st.expander("📄 View Filtered Loan Applications"):

    display_columns = [
        "SK_ID_CURR",
        "TARGET",
        "NAME_CONTRACT_TYPE",
        "CODE_GENDER",
        "AGE_GROUP",
        "INCOME_GROUP",
        "NAME_EDUCATION_TYPE",
        "EMPLOYMENT_GROUP",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "AMT_GOODS_PRICE",
        "WEEKDAY_APPR_PROCESS_START",
        "HOUR_APPR_PROCESS_START",
        "CREDIT_TO_INCOME",
        "CREDIT_TO_GOODS"
    ]

    available_columns = [
        column
        for column in display_columns
        if column in filtered.columns
    ]

    st.dataframe(
        filtered[available_columns].head(1000),
        use_container_width=True
    )

    csv = filtered[
        available_columns
    ].to_csv(index=False)

    st.download_button(
        label="⬇️ Download Filtered Applications",
        data=csv,
        file_name="loan_application_filtered_data.csv",
        mime="text/csv"
    )
