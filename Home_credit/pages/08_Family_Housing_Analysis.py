import streamlit as st
import pandas as pd
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Family & Housing Analysis",
    page_icon="🏠",
    layout="wide",
)

load_css()

st.title("🏠 Family & Housing Analysis")
st.caption(
    "Understanding household characteristics, housing ownership, "
    "family size, income capacity, and observed default behaviour."
)

st.divider()


# ============================================================
# LOAD DATA
# ============================================================

df = load_data()


# ============================================================
# BUSINESS OBJECTIVE
# ============================================================

with st.expander("🎯 Business Objective", expanded=True):
    st.markdown(
        """
        This page analyses household characteristics of Home Credit
        customers and explores how family and housing characteristics
        relate to income and observed default behaviour.

        The analysis covers:

        - Number of children
        - Family size
        - Family status
        - Housing type
        - Property ownership
        - Car ownership
        - Income per family member
        - Observed default rate

        The objective is to understand the typical household profile and
        identify differences in affordability and observed repayment risk
        across household groups.

        **Observed relationships are descriptive and do not imply causation.**
        """
    )


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Filters")


# Gender
gender_options = ["All"] + sorted(
    df["CODE_GENDER"].dropna().unique().tolist()
)

gender_sel = st.sidebar.selectbox(
    "Gender",
    gender_options
)


# Family Status
family_status_options = ["All"] + sorted(
    df["NAME_FAMILY_STATUS"].dropna().unique().tolist()
)

family_status_sel = st.sidebar.selectbox(
    "Family Status",
    family_status_options
)


# Housing Type
housing_options = ["All"] + sorted(
    df["NAME_HOUSING_TYPE"].dropna().unique().tolist()
)

housing_sel = st.sidebar.selectbox(
    "Housing Type",
    housing_options
)


# Property Ownership
property_options = ["All"] + sorted(
    df["FLAG_OWN_REALTY"].dropna().unique().tolist()
)

property_sel = st.sidebar.selectbox(
    "Property Ownership",
    property_options
)


# Car Ownership
car_options = ["All"] + sorted(
    df["FLAG_OWN_CAR"].dropna().unique().tolist()
)

car_sel = st.sidebar.selectbox(
    "Car Ownership",
    car_options
)


# Family Size Group
family_size_group_options = ["All"] + sorted(
    df["FAMILY_SIZE_GROUP"].dropna().unique().tolist()
)

family_size_group_sel = st.sidebar.selectbox(
    "Family Size Group",
    family_size_group_options
)


# Children Group
children_group_options = ["All"] + sorted(
    df["CHILDREN_GROUP"].dropna().unique().tolist()
)

children_group_sel = st.sidebar.selectbox(
    "Children Group",
    children_group_options
)


# Income Group
income_group_options = ["All"] + sorted(
    df["INCOME_GROUP"].dropna().unique().tolist()
)

income_group_sel = st.sidebar.selectbox(
    "Income Group",
    income_group_options
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


if gender_sel != "All":
    filtered = filtered[
        filtered["CODE_GENDER"] == gender_sel
    ]


if family_status_sel != "All":
    filtered = filtered[
        filtered["NAME_FAMILY_STATUS"] == family_status_sel
    ]


if housing_sel != "All":
    filtered = filtered[
        filtered["NAME_HOUSING_TYPE"] == housing_sel
    ]


if property_sel != "All":
    filtered = filtered[
        filtered["FLAG_OWN_REALTY"] == property_sel
    ]


if car_sel != "All":
    filtered = filtered[
        filtered["FLAG_OWN_CAR"] == car_sel
    ]


if family_size_group_sel != "All":
    filtered = filtered[
        filtered["FAMILY_SIZE_GROUP"] == family_size_group_sel
    ]


if children_group_sel != "All":
    filtered = filtered[
        filtered["CHILDREN_GROUP"] == children_group_sel
    ]


if income_group_sel != "All":
    filtered = filtered[
        filtered["INCOME_GROUP"] == income_group_sel
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
        "No customers match the selected filters. "
        "Please adjust the filters."
    )
    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

average_family_size = (
    filtered["CNT_FAM_MEMBERS"].mean()
)

average_children = (
    filtered["CNT_CHILDREN"].mean()
)


home_ownership_pct = (
    (filtered["FLAG_OWN_REALTY"] == "Y").mean() * 100
)


car_ownership_pct = (
    (filtered["FLAG_OWN_CAR"] == "Y").mean() * 100
)


housing_mode = (
    filtered["NAME_HOUSING_TYPE"]
    .dropna()
    .mode()
)

most_common_housing = (
    housing_mode.iloc[0]
    if not housing_mode.empty
    else "N/A"
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Household Portfolio Snapshot")

c1, c2, c3 = st.columns(3)

with c1:
    kpi_card(
        "Average Family Size",
        f"{average_family_size:.1f}"
    )

with c2:
    kpi_card(
        "Average Children",
        f"{average_children:.1f}"
    )

with c3:
    kpi_card(
        "Home Ownership",
        f"{home_ownership_pct:.1f}%"
    )


c4, c5 = st.columns(2)

with c4:
    kpi_card(
        "Car Ownership",
        f"{car_ownership_pct:.1f}%"
    )

with c5:
    kpi_card(
        "Most Common Housing Type",
        str(most_common_housing)
    )


st.divider()


# ============================================================
# FAMILY SIZE DISTRIBUTION
# ============================================================

st.subheader("👨‍👩‍👧 Family Size Distribution")

family_size_data = filtered[
    filtered["CNT_FAM_MEMBERS"].notna()
].copy()

family_size_limit = family_size_data[
    "CNT_FAM_MEMBERS"
].quantile(0.99)

family_size_chart = family_size_data[
    family_size_data["CNT_FAM_MEMBERS"] <= family_size_limit
]

fig = px.histogram(
    family_size_chart,
    x="CNT_FAM_MEMBERS",
    nbins=20,
    title="Distribution of Family Size",
    labels={
        "CNT_FAM_MEMBERS": "Number of Family Members"
    },
    color_discrete_sequence=[
        CHART_COLORS[0]
    ],
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CHILDREN DISTRIBUTION
# ============================================================

st.subheader("👶 Children Distribution")

children_counts = (
    filtered["CNT_CHILDREN"]
    .value_counts()
    .sort_index()
    .reset_index()
)

children_counts.columns = [
    "Children",
    "Customers"
]

fig = px.bar(
    children_counts,
    x="Children",
    y="Customers",
    title="Customers by Number of Children",
    labels={
        "Children": "Number of Children",
        "Customers": "Number of Customers"
    },
    color_discrete_sequence=[
        CHART_COLORS[1]
    ],
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# HOUSING TYPE DISTRIBUTION
# ============================================================

st.subheader("🏠 Housing Type Distribution")

housing_counts = (
    filtered["NAME_HOUSING_TYPE"]
    .value_counts()
    .reset_index()
)

housing_counts.columns = [
    "Housing Type",
    "Customers"
]

fig = px.bar(
    housing_counts,
    x="Customers",
    y="Housing Type",
    orientation="h",
    title="Customers by Housing Type",
    labels={
        "Customers": "Number of Customers"
    },
    color_discrete_sequence=[
        CHART_COLORS[2]
    ],
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# PROPERTY OWNERSHIP
# ============================================================

st.subheader("🏡 Property Ownership")

property_counts = (
    filtered["FLAG_OWN_REALTY"]
    .value_counts()
    .rename(
        {
            "Y": "Own Property",
            "N": "Do Not Own Property"
        }
    )
)

fig = px.pie(
    values=property_counts.values,
    names=property_counts.index,
    hole=0.55,
    title="Property Ownership Distribution",
    color_discrete_sequence=CHART_COLORS,
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CAR OWNERSHIP
# ============================================================

st.subheader("🚗 Car Ownership")

car_counts = (
    filtered["FLAG_OWN_CAR"]
    .value_counts()
    .rename(
        {
            "Y": "Own Car",
            "N": "Do Not Own Car"
        }
    )
)

fig = px.pie(
    values=car_counts.values,
    names=car_counts.index,
    hole=0.55,
    title="Car Ownership Distribution",
    color_discrete_sequence=CHART_COLORS,
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# FAMILY SIZE VS INCOME
# ============================================================

st.subheader("💰 Family Size vs Income")

family_income = filtered[
    [
        "CNT_FAM_MEMBERS",
        "AMT_INCOME_TOTAL",
        "NAME_FAMILY_STATUS"
    ]
].dropna()

# Cap display at 99th percentile to improve readability
income_limit = family_income[
    "AMT_INCOME_TOTAL"
].quantile(0.99)

family_income_chart = family_income[
    family_income["AMT_INCOME_TOTAL"] <= income_limit
]

fig = px.box(
    family_income_chart,
    x="CNT_FAM_MEMBERS",
    y="AMT_INCOME_TOTAL",
    title="Income Distribution by Family Size",
    labels={
        "CNT_FAM_MEMBERS": "Family Size",
        "AMT_INCOME_TOTAL": "Annual Income"
    },
    color_discrete_sequence=[
        CHART_COLORS[3]
    ],
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# FAMILY SIZE VS DEFAULT RATE
# ============================================================

st.subheader("⚠️ Family Size vs Observed Default Rate")

family_risk = (
    filtered.groupby(
        "FAMILY_SIZE_GROUP"
    )
    .agg(
        Customers=("TARGET", "size"),
        Defaults=("TARGET", "sum"),
        Default_Rate=("TARGET", "mean")
    )
    .reset_index()
)

family_risk["Default_Rate"] *= 100

fig = px.bar(
    family_risk,
    x="FAMILY_SIZE_GROUP",
    y="Default_Rate",
    title="Observed Default Rate by Family Size Group",
    labels={
        "FAMILY_SIZE_GROUP": "Family Size Group",
        "Default_Rate": "Observed Default Rate (%)"
    },
    text="Default_Rate",
    color_discrete_sequence=[
        CHART_COLORS[0]
    ],
)

fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# INCOME PER FAMILY MEMBER
# ============================================================

st.subheader("💵 Income per Family Member")

income_family = filtered[
    filtered["INCOME_PER_FAMILY_MEMBER"].notna()
].copy()

income_family_limit = income_family[
    "INCOME_PER_FAMILY_MEMBER"
].quantile(0.99)

income_family_chart = income_family[
    income_family["INCOME_PER_FAMILY_MEMBER"]
    <= income_family_limit
]

fig = px.histogram(
    income_family_chart,
    x="INCOME_PER_FAMILY_MEMBER",
    nbins=40,
    title="Income per Family Member Distribution — Up to 99th Percentile",
    labels={
        "INCOME_PER_FAMILY_MEMBER":
            "Income per Family Member"
    },
    color_discrete_sequence=[
        CHART_COLORS[1]
    ],
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# FAMILY STATUS VS DEFAULT
# ============================================================

st.subheader("👨‍👩‍👧 Family Status vs Observed Default Rate")

family_status_risk = (
    filtered.groupby(
        "NAME_FAMILY_STATUS"
    )
    .agg(
        Customers=("TARGET", "size"),
        Defaults=("TARGET", "sum"),
        Default_Rate=("TARGET", "mean")
    )
    .reset_index()
)

family_status_risk["Default_Rate"] *= 100

family_status_risk = family_status_risk.sort_values(
    "Default_Rate"
)

fig = px.bar(
    family_status_risk,
    x="Default_Rate",
    y="NAME_FAMILY_STATUS",
    orientation="h",
    title="Observed Default Rate by Family Status",
    labels={
        "NAME_FAMILY_STATUS": "Family Status",
        "Default_Rate": "Observed Default Rate (%)"
    },
    color_discrete_sequence=[
        CHART_COLORS[2]
    ],
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# HOUSING TYPE VS DEFAULT
# ============================================================

st.subheader("🏠 Housing Type vs Observed Default Rate")

housing_risk = (
    filtered.groupby(
        "NAME_HOUSING_TYPE"
    )
    .agg(
        Customers=("TARGET", "size"),
        Default_Rate=("TARGET", "mean")
    )
    .reset_index()
)

housing_risk["Default_Rate"] *= 100

housing_risk = housing_risk.sort_values(
    "Default_Rate"
)

fig = px.bar(
    housing_risk,
    x="Default_Rate",
    y="NAME_HOUSING_TYPE",
    orientation="h",
    title="Observed Default Rate by Housing Type",
    labels={
        "NAME_HOUSING_TYPE": "Housing Type",
        "Default_Rate": "Observed Default Rate (%)"
    },
    color_discrete_sequence=[
        CHART_COLORS[3]
    ],
)

fig.update_layout(
    template="plotly_white",
    margin=dict(
        t=50,
        l=10,
        r=10,
        b=10
    ),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# FAMILY SIZE STATISTICAL SUMMARY
# ============================================================

st.divider()

st.subheader("📋 Family & Housing Statistical Summary")

family_summary = (
    filtered.groupby(
        "FAMILY_SIZE_GROUP"
    )
    .agg(
        Customers=("SK_ID_CURR", "count"),
        Average_Family_Size=(
            "CNT_FAM_MEMBERS",
            "mean"
        ),
        Average_Children=(
            "CNT_CHILDREN",
            "mean"
        ),
        Average_Income=(
            "AMT_INCOME_TOTAL",
            "mean"
        ),
        Average_Income_Per_Family_Member=(
            "INCOME_PER_FAMILY_MEMBER",
            "mean"
        ),
        Average_Credit=(
            "AMT_CREDIT",
            "mean"
        ),
        Defaults=(
            "TARGET",
            "sum"
        ),
        Default_Rate=(
            "TARGET",
            "mean"
        )
    )
    .reset_index()
)

family_summary["Default_Rate"] *= 100

st.dataframe(
    family_summary.style.format(
        {
            "Customers": "{:,.0f}",
            "Average_Family_Size": "{:.1f}",
            "Average_Children": "{:.1f}",
            "Average_Income": "₹{:,.0f}",
            "Average_Income_Per_Family_Member": "₹{:,.0f}",
            "Average_Credit": "₹{:,.0f}",
            "Defaults": "{:,.0f}",
            "Default_Rate": "{:.2f}%",
        }
    ),
    use_container_width=True
)


# ============================================================
# KEY OBSERVATIONS
# ============================================================

st.subheader("🔍 Key Observations")

highest_family_risk = (
    family_risk.loc[
        family_risk["Default_Rate"].idxmax(),
        "FAMILY_SIZE_GROUP"
    ]
)

highest_family_risk_rate = (
    family_risk["Default_Rate"].max()
)


highest_family_status = (
    family_status_risk.loc[
        family_status_risk["Default_Rate"].idxmax(),
        "NAME_FAMILY_STATUS"
    ]
)

highest_family_status_rate = (
    family_status_risk["Default_Rate"].max()
)


highest_housing_risk = (
    housing_risk.loc[
        housing_risk["Default_Rate"].idxmax(),
        "NAME_HOUSING_TYPE"
    ]
)

highest_housing_risk_rate = (
    housing_risk["Default_Rate"].max()
)


st.markdown(
    f"""
- The average family size in the filtered portfolio is
  **{average_family_size:.1f} members**.
- Customers have an average of **{average_children:.1f} children**.
- Approximately **{home_ownership_pct:.1f}%** of filtered customers report
  property ownership.
- Approximately **{car_ownership_pct:.1f}%** report car ownership.
- The family-size group with the highest observed default rate is
  **{highest_family_risk}**, at approximately
  **{highest_family_risk_rate:.1f}%**.
- The family-status category with the highest observed default rate is
  **{highest_family_status}**, at approximately
  **{highest_family_status_rate:.1f}%**.
- The housing type with the highest observed default rate is
  **{highest_housing_risk}**, at approximately
  **{highest_housing_risk_rate:.1f}%**.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown(
    """
### 1. Family size provides household context

Family size helps describe the number of people potentially supported by a
customer's income and therefore provides useful affordability context.

### 2. Income per family member gives a more informative household view

Two customers with identical income may have very different household
financial capacity if their family sizes differ.

### 3. Children and family size should be analysed together

The number of children can influence household expenses, while total family
size provides a broader measure of household composition.

### 4. Housing characteristics provide additional customer segmentation

Housing type and property ownership can help describe the financial and
socio-economic composition of the portfolio.

### 5. Ownership variables should not be interpreted as direct risk indicators

Car or property ownership may correlate with other customer characteristics,
but observed differences should not be interpreted as causal relationships.

### 6. Default rates should be compared alongside customer counts

A small household category can show a high percentage because of a small
number of observations. Customer volume should therefore always be reviewed
alongside the rate.
"""
)


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader("✅ Recommendations")

st.markdown(
    """
1. **Use income per family member alongside total income** when evaluating
   household affordability.

2. **Monitor family-size segments** for differences in credit exposure and
   observed default rates.

3. **Combine household analysis with credit-to-income ratios** on the
   affordability page rather than relying on family characteristics alone.

4. **Track housing-type composition** to understand how the portfolio changes
   across customer segments.

5. **Review family groups with unusually high observed default rates** while
   considering their customer counts.

6. **Avoid treating property or car ownership as standalone risk measures.**
   Use them as descriptive segmentation variables.

7. **Monitor changes in household composition over time** as part of portfolio
   reporting.
"""
)


# ============================================================
# DETAILED FILTERED DATA
# ============================================================

st.divider()

with st.expander("📄 View Filtered Customer Records"):

    display_columns = [
        "SK_ID_CURR",
        "TARGET",
        "CODE_GENDER",
        "CNT_CHILDREN",
        "CHILDREN_GROUP",
        "CNT_FAM_MEMBERS",
        "FAMILY_SIZE_GROUP",
        "NAME_FAMILY_STATUS",
        "NAME_HOUSING_TYPE",
        "FLAG_OWN_CAR",
        "FLAG_OWN_REALTY",
        "AMT_INCOME_TOTAL",
        "INCOME_PER_FAMILY_MEMBER",
        "INCOME_GROUP",
        "AMT_CREDIT",
        "AMT_ANNUITY",
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
        label="⬇️ Download Filtered Data",
        data=csv,
        file_name="family_housing_filtered_data.csv",
        mime="text/csv",
    )