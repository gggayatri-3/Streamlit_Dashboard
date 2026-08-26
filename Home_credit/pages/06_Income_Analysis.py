import streamlit as st
import pandas as pd
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Income Analysis",
    page_icon="💰",
    layout="wide",
)

load_css()

st.title("💰 Income Analysis")
st.caption(
    "Understanding customer income distribution and its relationship with lending and observed default behaviour."
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
        This page analyses the income profile of Home Credit customers and
        examines how income relates to credit exposure and observed default
        behaviour.

        The analysis focuses on:

        - Income distribution
        - Income groups
        - Income per family member
        - Education
        - Occupation
        - Income type
        - Credit exposure
        - Observed default rates

        The objective is to identify which income segments borrow the most,
        which segments show higher observed default rates, and where loan
        burden may be concentrated.

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


# Income Group
income_group_options = ["All"] + sorted(
    df["INCOME_GROUP"].dropna().unique().tolist()
)

income_group_sel = st.sidebar.selectbox(
    "Income Group",
    income_group_options
)


# Education
education_options = ["All"] + sorted(
    df["NAME_EDUCATION_TYPE"].dropna().unique().tolist()
)

education_sel = st.sidebar.selectbox(
    "Education",
    education_options
)


# Occupation
occupation_values = (
    df["OCCUPATION_TYPE"]
    .dropna()
    .unique()
    .tolist()
)

occupation_options = ["All"] + sorted(
    occupation_values
)

occupation_sel = st.sidebar.selectbox(
    "Occupation",
    occupation_options
)


# Income Type
income_type_options = ["All"] + sorted(
    df["NAME_INCOME_TYPE"].dropna().unique().tolist()
)

income_type_sel = st.sidebar.selectbox(
    "Income Type",
    income_type_options
)


# Age Group
age_group_options = ["All"] + sorted(
    df["AGE_GROUP"].dropna().unique().tolist()
)

age_group_sel = st.sidebar.selectbox(
    "Age Group",
    age_group_options
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


if income_group_sel != "All":
    filtered = filtered[
        filtered["INCOME_GROUP"] == income_group_sel
    ]


if education_sel != "All":
    filtered = filtered[
        filtered["NAME_EDUCATION_TYPE"] == education_sel
    ]


if occupation_sel != "All":
    filtered = filtered[
        filtered["OCCUPATION_TYPE"] == occupation_sel
    ]


if income_type_sel != "All":
    filtered = filtered[
        filtered["NAME_INCOME_TYPE"] == income_type_sel
    ]


if age_group_sel != "All":
    filtered = filtered[
        filtered["AGE_GROUP"] == age_group_sel
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

average_income = filtered["AMT_INCOME_TOTAL"].mean()
median_income = filtered["AMT_INCOME_TOTAL"].median()
maximum_income = filtered["AMT_INCOME_TOTAL"].max()

average_income_family = (
    filtered["INCOME_PER_FAMILY_MEMBER"].mean()
)

largest_income_group_series = (
    filtered["INCOME_GROUP"]
    .dropna()
    .value_counts()
)

largest_income_group = (
    largest_income_group_series.index[0]
    if not largest_income_group_series.empty
    else "N/A"
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Income Portfolio Snapshot")

c1, c2, c3 = st.columns(3)

with c1:
    kpi_card(
        "Average Income",
        f"₹{average_income:,.0f}"
    )

with c2:
    kpi_card(
        "Median Income",
        f"₹{median_income:,.0f}"
    )

with c3:
    kpi_card(
        "Maximum Income",
        f"₹{maximum_income:,.0f}"
    )


c4, c5 = st.columns(2)

with c4:
    kpi_card(
        "Avg Income / Family Member",
        f"₹{average_income_family:,.0f}"
    )

with c5:
    kpi_card(
        "Largest Income Group",
        str(largest_income_group)
    )


st.divider()


# ============================================================
# INCOME HISTOGRAM
# ============================================================

st.subheader("💵 Income Distribution")

income_plot = filtered[
    filtered["AMT_INCOME_TOTAL"].notna()
].copy()

# Use 99th percentile only for chart readability.
income_limit = income_plot[
    "AMT_INCOME_TOTAL"
].quantile(0.99)

income_chart = income_plot[
    income_plot["AMT_INCOME_TOTAL"] <= income_limit
]

fig = px.histogram(
    income_chart,
    x="AMT_INCOME_TOTAL",
    nbins=50,
    title="Customer Income Distribution — Up to 99th Percentile",
    labels={
        "AMT_INCOME_TOTAL": "Annual Income"
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

st.caption(
    f"Chart displayed through the 99th percentile "
    f"(₹{income_limit:,.0f}) to improve readability. "
    "Underlying calculations use all filtered records."
)


# ============================================================
# INCOME GROUP DISTRIBUTION
# ============================================================

st.subheader("📊 Income Group Distribution")

income_group_counts = (
    filtered["INCOME_GROUP"]
    .value_counts()
    .reset_index()
)

income_group_counts.columns = [
    "Income Group",
    "Customers"
]

fig = px.bar(
    income_group_counts,
    x="Income Group",
    y="Customers",
    title="Customers by Income Group",
    labels={
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
# INCOME BY EDUCATION
# ============================================================

st.subheader("🎓 Income by Education")

education_income = filtered[
    [
        "NAME_EDUCATION_TYPE",
        "AMT_INCOME_TOTAL"
    ]
].dropna()

fig = px.box(
    education_income,
    x="NAME_EDUCATION_TYPE",
    y="AMT_INCOME_TOTAL",
    title="Income Distribution Across Education Levels",
    labels={
        "NAME_EDUCATION_TYPE": "Education",
        "AMT_INCOME_TOTAL": "Annual Income"
    },
    color_discrete_sequence=[
        CHART_COLORS[2]
    ],
)

fig.update_layout(
    template="plotly_white",
    xaxis_tickangle=-30,
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
# INCOME BY OCCUPATION
# ============================================================

st.subheader("💼 Income by Occupation")

occupation_income = (
    filtered.groupby(
        "OCCUPATION_TYPE"
    )["AMT_INCOME_TOTAL"]
    .median()
    .sort_values()
    .reset_index()
)

occupation_income.columns = [
    "Occupation",
    "Median Income"
]

fig = px.bar(
    occupation_income,
    x="Median Income",
    y="Occupation",
    orientation="h",
    title="Median Income by Occupation",
    labels={
        "Median Income": "Median Annual Income"
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
# INCOME BY INCOME TYPE
# ============================================================

st.subheader("🏢 Income by Income Type")

income_type_data = filtered[
    [
        "NAME_INCOME_TYPE",
        "AMT_INCOME_TOTAL"
    ]
].dropna()

fig = px.box(
    income_type_data,
    x="NAME_INCOME_TYPE",
    y="AMT_INCOME_TOTAL",
    title="Income Distribution by Income Type",
    labels={
        "NAME_INCOME_TYPE": "Income Type",
        "AMT_INCOME_TOTAL": "Annual Income"
    },
    color_discrete_sequence=[
        CHART_COLORS[0]
    ],
)

fig.update_layout(
    template="plotly_white",
    xaxis_tickangle=-30,
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
# INCOME VS CREDIT
# ============================================================

st.subheader("💳 Income vs Credit")

scatter_df = filtered[
    [
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "TARGET",
        "INCOME_GROUP",
        "NAME_INCOME_TYPE"
    ]
].dropna()


# Limit plotted points for browser performance.
if len(scatter_df) > 15000:
    scatter_df = scatter_df.sample(
        15000,
        random_state=42
    )


fig = px.scatter(
    scatter_df,
    x="AMT_INCOME_TOTAL",
    y="AMT_CREDIT",
    color="TARGET",
    hover_data=[
        "INCOME_GROUP",
        "NAME_INCOME_TYPE"
    ],
    title="Customer Income vs Credit Amount",
    labels={
        "AMT_INCOME_TOTAL": "Annual Income",
        "AMT_CREDIT": "Credit Amount",
        "TARGET": "Default Status"
    },
    color_discrete_sequence=CHART_COLORS,
    opacity=0.55,
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
# INCOME GROUP VS DEFAULT RATE
# ============================================================

st.subheader("⚠️ Income Group vs Observed Default Rate")

income_default = (
    filtered.groupby(
        "INCOME_GROUP"
    )
    .agg(
        Customers=("TARGET", "size"),
        Defaults=("TARGET", "sum"),
        Default_Rate=("TARGET", "mean")
    )
    .reset_index()
)

income_default["Default_Rate"] *= 100

income_default = income_default.sort_values(
    "Default_Rate"
)

fig = px.bar(
    income_default,
    x="INCOME_GROUP",
    y="Default_Rate",
    title="Observed Default Rate by Income Group",
    labels={
        "INCOME_GROUP": "Income Group",
        "Default_Rate": "Observed Default Rate (%)"
    },
    text="Default_Rate",
    color_discrete_sequence=[
        CHART_COLORS[1]
    ],
)

fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    yaxis_title="Observed Default Rate (%)",
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
# INCOME GROUP SUMMARY
# ============================================================

st.divider()

st.subheader("📋 Income Group Statistical Summary")

income_summary = (
    filtered.groupby(
        "INCOME_GROUP"
    )
    .agg(
        Customers=("SK_ID_CURR", "count"),
        Average_Income=("AMT_INCOME_TOTAL", "mean"),
        Median_Income=("AMT_INCOME_TOTAL", "median"),
        Average_Credit=("AMT_CREDIT", "mean"),
        Median_Credit=("AMT_CREDIT", "median"),
        Average_Income_Per_Family_Member=(
            "INCOME_PER_FAMILY_MEMBER",
            "mean"
        ),
        Defaults=("TARGET", "sum"),
        Default_Rate=("TARGET", "mean")
    )
    .reset_index()
)

income_summary["Default_Rate"] *= 100

st.dataframe(
    income_summary.style.format(
        {
            "Customers": "{:,.0f}",
            "Average_Income": "₹{:,.0f}",
            "Median_Income": "₹{:,.0f}",
            "Average_Credit": "₹{:,.0f}",
            "Median_Credit": "₹{:,.0f}",
            "Average_Income_Per_Family_Member": "₹{:,.0f}",
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

highest_default_group = (
    income_default.loc[
        income_default["Default_Rate"].idxmax(),
        "INCOME_GROUP"
    ]
)

highest_default_rate = (
    income_default["Default_Rate"].max()
)

largest_borrowing_group = (
    income_summary.loc[
        income_summary["Average_Credit"].idxmax(),
        "INCOME_GROUP"
    ]
)

largest_borrowing_credit = (
    income_summary["Average_Credit"].max()
)


st.markdown(
    f"""
- The average income in the current filtered portfolio is
  **₹{average_income:,.0f}**, while the median is
  **₹{median_income:,.0f}**.
- **{largest_income_group}** is the largest income segment by customer count.
- The highest observed default rate among income groups is
  **{highest_default_rate:.2f}%**, recorded in the **{highest_default_group}**
  group.
- **{largest_borrowing_group}** has the highest average credit exposure at
  approximately **₹{largest_borrowing_credit:,.0f}**.
- The difference between average and median income should be considered when
  assessing the income distribution because extreme values can influence the
  mean.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown(
    """
### 1. Income distribution is an important portfolio characteristic

Income determines the financial capacity profile of customers and should be
examined alongside credit exposure rather than in isolation.

### 2. Income segments can have different credit exposure

Comparing income groups with average and median credit helps identify where
larger lending amounts are concentrated.

### 3. Income group size must be considered when interpreting defaults

A large income group may naturally contain more default customers simply
because it contains more customers. Default **rates**, rather than only
default counts, provide a fairer comparison.

### 4. Income and education can show different distribution patterns

Income levels may vary considerably across education categories. These
differences provide descriptive portfolio context.

### 5. Income type provides another dimension of financial profile

Different income types may have different income distributions and customer
volumes. These patterns should be considered when analysing affordability.

### 6. Income alone should not be treated as a measure of risk

Observed default behaviour should be considered together with credit burden,
employment stability and repayment behaviour on later pages.
"""
)


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader("✅ Recommendations")

st.markdown(
    """
1. **Monitor credit exposure across income groups** to identify segments
   carrying disproportionately large loan amounts.

2. **Use median income alongside average income** when reporting portfolio
   characteristics because financial distributions can be skewed.

3. **Compare income groups using default rates rather than default counts**
   when assessing observed risk differences.

4. **Combine income analysis with affordability ratios** on the Credit
   Affordability page to identify customers with potentially high loan burden.

5. **Track income-group composition over time** to identify changes in the
   portfolio's customer mix.

6. **Avoid making causal conclusions from income-default relationships.**
   Observed differences should be investigated alongside other customer and
   repayment characteristics.
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
        "AGE_YEARS",
        "AGE_GROUP",
        "AMT_INCOME_TOTAL",
        "INCOME_GROUP",
        "INCOME_PER_FAMILY_MEMBER",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "NAME_EDUCATION_TYPE",
        "NAME_INCOME_TYPE",
        "OCCUPATION_TYPE",
        "CNT_CHILDREN",
        "CNT_FAM_MEMBERS",
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

    csv = filtered[available_columns].to_csv(
        index=False
    )

    st.download_button(
        label="⬇️ Download Filtered Data",
        data=csv,
        file_name="income_analysis_filtered_data.csv",
        mime="text/csv",
    )