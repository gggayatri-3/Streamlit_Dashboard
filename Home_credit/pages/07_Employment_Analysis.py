import streamlit as st
import pandas as pd
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Employment Analysis",
    page_icon="💼",
    layout="wide",
)

load_css()

st.title("💼 Employment Analysis")
st.caption(
    "Understanding employment stability and its relationship with income, "
    "credit exposure, and observed default behaviour."
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
        This page analyses the employment characteristics of Home Credit
        customers and explores how employment stability relates to income,
        credit exposure, and observed default behaviour.

        The analysis focuses on:

        - Employment duration
        - Employment groups
        - Occupation
        - Organization type
        - Income
        - Credit exposure
        - Observed default rate

        **Important:** `DAYS_EMPLOYED` contains unusual values in the original
        Home Credit dataset. These values should be investigated before using
        employment duration as a business measure.

        This page is descriptive EDA only. Observed relationships do not imply
        causation.
        """
    )


# ============================================================
# ABNORMAL DAYS_EMPLOYED CHECK
# ============================================================

st.subheader("⚠️ Employment Data Quality Check")

special_employment_count = (
    df["DAYS_EMPLOYED"] == 365243
).sum()

special_employment_percentage = (
    special_employment_count / len(df) * 100
)

qc1, qc2, qc3 = st.columns(3)

with qc1:
    kpi_card(
        "Total Customers",
        f"{len(df):,}"
    )

with qc2:
    kpi_card(
        "DAYS_EMPLOYED = 365243",
        f"{special_employment_count:,}"
    )

with qc3:
    kpi_card(
        "Special Value %",
        f"{special_employment_percentage:.2f}%"
    )

st.info(
    "The value 365243 is a known special/placeholder value in the Home "
    "Credit dataset and should not be interpreted literally as 365243 days "
    "of employment."
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


# Employment Group
employment_group_options = ["All"] + sorted(
    df["EMPLOYMENT_GROUP"].dropna().unique().tolist()
)

employment_group_sel = st.sidebar.selectbox(
    "Employment Group",
    employment_group_options
)


# Occupation
occupation_options = ["All"] + sorted(
    df["OCCUPATION_TYPE"].dropna().unique().tolist()
)

occupation_sel = st.sidebar.selectbox(
    "Occupation",
    occupation_options
)


# Organization Type
organization_options = ["All"] + sorted(
    df["ORGANIZATION_TYPE"].dropna().unique().tolist()
)

organization_sel = st.sidebar.selectbox(
    "Organization Type",
    organization_options
)


# Income Group
income_group_options = ["All"] + sorted(
    df["INCOME_GROUP"].dropna().unique().tolist()
)

income_group_sel = st.sidebar.selectbox(
    "Income Group",
    income_group_options
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

if employment_group_sel != "All":
    filtered = filtered[
        filtered["EMPLOYMENT_GROUP"] == employment_group_sel
    ]

if occupation_sel != "All":
    filtered = filtered[
        filtered["OCCUPATION_TYPE"] == occupation_sel
    ]

if organization_sel != "All":
    filtered = filtered[
        filtered["ORGANIZATION_TYPE"] == organization_sel
    ]

if income_group_sel != "All":
    filtered = filtered[
        filtered["INCOME_GROUP"] == income_group_sel
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

average_employment = (
    filtered["EMPLOYMENT_YEARS"].mean()
)

median_employment = (
    filtered["EMPLOYMENT_YEARS"].median()
)


occupation_mode = (
    filtered["OCCUPATION_TYPE"]
    .dropna()
    .mode()
)

most_common_occupation = (
    occupation_mode.iloc[0]
    if not occupation_mode.empty
    else "N/A"
)


organization_mode = (
    filtered["ORGANIZATION_TYPE"]
    .dropna()
    .mode()
)

most_common_organization = (
    organization_mode.iloc[0]
    if not organization_mode.empty
    else "N/A"
)


employment_default = (
    filtered.groupby(
        "EMPLOYMENT_GROUP"
    )["TARGET"]
    .mean()
    .dropna()
    * 100
)

highest_default_group = (
    employment_default.idxmax()
    if not employment_default.empty
    else "N/A"
)

highest_default_rate = (
    employment_default.max()
    if not employment_default.empty
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Employment Portfolio Snapshot")

c1, c2, c3 = st.columns(3)

with c1:
    kpi_card(
        "Average Employment",
        f"{average_employment:.1f} years"
    )

with c2:
    kpi_card(
        "Median Employment",
        f"{median_employment:.1f} years"
    )

with c3:
    kpi_card(
        "Most Common Occupation",
        str(most_common_occupation)
    )


c4, c5 = st.columns(2)

with c4:
    kpi_card(
        "Most Common Organization",
        str(most_common_organization)
    )

with c5:
    kpi_card(
        "Highest Default Employment Group",
        f"{highest_default_group} ({highest_default_rate:.1f}%)"
    )


st.divider()


# ============================================================
# EMPLOYMENT YEARS DISTRIBUTION
# ============================================================

st.subheader("⏳ Employment Years Distribution")

employment_plot = filtered[
    filtered["EMPLOYMENT_YEARS"].notna()
].copy()

# Keep extreme values from dominating the visual.
employment_limit = employment_plot[
    "EMPLOYMENT_YEARS"
].quantile(0.99)

employment_chart = employment_plot[
    employment_plot["EMPLOYMENT_YEARS"] <= employment_limit
]

fig = px.histogram(
    employment_chart,
    x="EMPLOYMENT_YEARS",
    nbins=40,
    title="Employment Duration Distribution — Up to 99th Percentile",
    labels={
        "EMPLOYMENT_YEARS": "Employment Years"
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
    "The chart is limited to the 99th percentile for readability. "
    "The underlying dataset is not altered."
)


# ============================================================
# EMPLOYMENT GROUP DISTRIBUTION
# ============================================================

st.subheader("📊 Employment Group Distribution")

employment_counts = (
    filtered["EMPLOYMENT_GROUP"]
    .value_counts()
    .reset_index()
)

employment_counts.columns = [
    "Employment Group",
    "Customers"
]

fig = px.bar(
    employment_counts,
    x="Employment Group",
    y="Customers",
    title="Customers by Employment Group",
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
# DEFAULT RATE BY EMPLOYMENT GROUP
# ============================================================

st.subheader("⚠️ Default Rate by Employment Group")

employment_risk = (
    filtered.groupby(
        "EMPLOYMENT_GROUP"
    )
    .agg(
        Customers=("TARGET", "size"),
        Defaults=("TARGET", "sum"),
        Default_Rate=("TARGET", "mean")
    )
    .reset_index()
)

employment_risk["Default_Rate"] *= 100

employment_risk = employment_risk.sort_values(
    "Default_Rate"
)

fig = px.bar(
    employment_risk,
    x="EMPLOYMENT_GROUP",
    y="Default_Rate",
    title="Observed Default Rate by Employment Group",
    labels={
        "EMPLOYMENT_GROUP": "Employment Group",
        "Default_Rate": "Observed Default Rate (%)"
    },
    text="Default_Rate",
    color_discrete_sequence=[
        CHART_COLORS[2]
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
# OCCUPATION VS DEFAULT RATE
# ============================================================

st.subheader("👔 Occupation vs Observed Default Rate")

occupation_risk = (
    filtered.dropna(
        subset=["OCCUPATION_TYPE"]
    )
    .groupby("OCCUPATION_TYPE")
    .agg(
        Customers=("TARGET", "size"),
        Default_Rate=("TARGET", "mean")
    )
    .reset_index()
)

occupation_risk["Default_Rate"] *= 100

occupation_risk = occupation_risk.sort_values(
    "Default_Rate"
)

fig = px.bar(
    occupation_risk,
    x="Default_Rate",
    y="OCCUPATION_TYPE",
    orientation="h",
    title="Observed Default Rate by Occupation",
    labels={
        "OCCUPATION_TYPE": "Occupation",
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
# ORGANIZATION TYPE VS DEFAULT
# ============================================================

st.subheader("🏢 Organization Type vs Observed Default Rate")

organization_risk = (
    filtered.dropna(
        subset=["ORGANIZATION_TYPE"]
    )
    .groupby("ORGANIZATION_TYPE")
    .agg(
        Customers=("TARGET", "size"),
        Default_Rate=("TARGET", "mean")
    )
    .reset_index()
)

organization_risk["Default_Rate"] *= 100

# Show organizations with at least 100 customers
organization_risk_display = organization_risk[
    organization_risk["Customers"] >= 100
].sort_values(
    "Default_Rate"
)

fig = px.bar(
    organization_risk_display,
    x="Default_Rate",
    y="ORGANIZATION_TYPE",
    orientation="h",
    title="Observed Default Rate by Organization Type (100+ Customers)",
    labels={
        "ORGANIZATION_TYPE": "Organization Type",
        "Default_Rate": "Observed Default Rate (%)"
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
# EMPLOYMENT YEARS VS INCOME
# ============================================================

st.subheader("💰 Employment Years vs Income")

employment_income = filtered[
    [
        "EMPLOYMENT_YEARS",
        "AMT_INCOME_TOTAL",
        "TARGET",
        "OCCUPATION_TYPE"
    ]
].dropna(
    subset=[
        "EMPLOYMENT_YEARS",
        "AMT_INCOME_TOTAL"
    ]
)

if len(employment_income) > 15000:
    employment_income = employment_income.sample(
        15000,
        random_state=42
    )

fig = px.scatter(
    employment_income,
    x="EMPLOYMENT_YEARS",
    y="AMT_INCOME_TOTAL",
    color="TARGET",
    hover_data=[
        "OCCUPATION_TYPE"
    ],
    title="Employment Duration vs Annual Income",
    labels={
        "EMPLOYMENT_YEARS": "Employment Years",
        "AMT_INCOME_TOTAL": "Annual Income",
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
# EMPLOYMENT YEARS VS CREDIT
# ============================================================

st.subheader("💳 Employment Years vs Credit")

employment_credit = filtered[
    [
        "EMPLOYMENT_YEARS",
        "AMT_CREDIT",
        "TARGET",
        "INCOME_GROUP"
    ]
].dropna(
    subset=[
        "EMPLOYMENT_YEARS",
        "AMT_CREDIT"
    ]
)

if len(employment_credit) > 15000:
    employment_credit = employment_credit.sample(
        15000,
        random_state=42
    )

fig = px.scatter(
    employment_credit,
    x="EMPLOYMENT_YEARS",
    y="AMT_CREDIT",
    color="TARGET",
    hover_data=[
        "INCOME_GROUP"
    ],
    title="Employment Duration vs Credit Amount",
    labels={
        "EMPLOYMENT_YEARS": "Employment Years",
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
# EMPLOYMENT GROUP SUMMARY TABLE
# ============================================================

st.divider()

st.subheader("📋 Employment Group Statistical Summary")

employment_summary = (
    filtered.groupby(
        "EMPLOYMENT_GROUP"
    )
    .agg(
        Customers=("SK_ID_CURR", "count"),
        Average_Employment_Years=(
            "EMPLOYMENT_YEARS",
            "mean"
        ),
        Median_Employment_Years=(
            "EMPLOYMENT_YEARS",
            "median"
        ),
        Average_Income=(
            "AMT_INCOME_TOTAL",
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

employment_summary["Default_Rate"] *= 100

st.dataframe(
    employment_summary.style.format(
        {
            "Customers": "{:,.0f}",
            "Average_Employment_Years": "{:.1f}",
            "Median_Employment_Years": "{:.1f}",
            "Average_Income": "₹{:,.0f}",
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

highest_occupation = (
    occupation_risk.loc[
        occupation_risk["Default_Rate"].idxmax(),
        "OCCUPATION_TYPE"
    ]
    if not occupation_risk.empty
    else "N/A"
)

highest_occupation_rate = (
    occupation_risk["Default_Rate"].max()
    if not occupation_risk.empty
    else 0
)

highest_organization = (
    organization_risk_display.loc[
        organization_risk_display["Default_Rate"].idxmax(),
        "ORGANIZATION_TYPE"
    ]
    if not organization_risk_display.empty
    else "N/A"
)

highest_organization_rate = (
    organization_risk_display["Default_Rate"].max()
    if not organization_risk_display.empty
    else 0
)


st.markdown(
    f"""
- The average employment duration in the current filtered portfolio is
  **{average_employment:.1f} years**, while the median is
  **{median_employment:.1f} years**.
- The employment group with the highest observed default rate is
  **{highest_default_group}**, at approximately
  **{highest_default_rate:.1f}%**.
- Among occupations represented in the filtered data,
  **{highest_occupation}** has the highest observed default rate at
  approximately **{highest_occupation_rate:.1f}%**.
- Among organization types with at least 100 customers,
  **{highest_organization}** has the highest observed default rate at
  approximately **{highest_organization_rate:.1f}%**.
- Employment duration should be interpreted together with income and credit
  exposure rather than being treated as an independent measure of risk.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown(
    """
### 1. Employment stability provides useful portfolio context

Employment duration helps describe the financial stability profile of
customers and should be considered alongside income and credit exposure.

### 2. Short employment histories may require closer analysis

Customers in shorter employment-duration groups can be compared with longer
tenure groups to identify differences in observed default rates.

### 3. Occupation groups can have different observed outcomes

Differences between occupations may reflect differences in income distribution,
employment patterns, or customer composition.

### 4. Organization type provides another segmentation dimension

Different organization types may show different customer volumes and observed
default rates. Small groups should be interpreted carefully because their rates
can be unstable.

### 5. Employment and income should be analysed together

Employment duration does not provide a complete picture of financial capacity.
Income and credit exposure provide important additional context.

### 6. Employment data quality matters

The special `DAYS_EMPLOYED = 365243` value demonstrates why raw employment
fields should be validated before being interpreted as actual employment
duration.
"""
)


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader("✅ Recommendations")

st.markdown(
    """
1. **Monitor employment-duration groups** for differences in observed default
   rates.

2. **Combine employment stability with affordability analysis** rather than
   evaluating employment duration alone.

3. **Review occupation-level patterns** when substantial differences in
   observed default rates appear.

4. **Apply minimum customer-count thresholds** when comparing organization
   types to avoid over-interpreting very small groups.

5. **Maintain a dedicated data-quality rule for `DAYS_EMPLOYED = 365243`**
   so the special value is not interpreted as literal employment duration.

6. **Track employment-group composition over time** to identify changes in
   the customer portfolio.

7. **Use employment patterns as descriptive evidence**, not as proof that
   employment duration causes default.
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
        "DAYS_EMPLOYED",
        "EMPLOYMENT_YEARS",
        "EMPLOYMENT_GROUP",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "NAME_INCOME_TYPE",
        "OCCUPATION_TYPE",
        "ORGANIZATION_TYPE",
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
        file_name="employment_analysis_filtered_data.csv",
        mime="text/csv",
    )