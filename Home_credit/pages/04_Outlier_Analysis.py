import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Outlier & Distribution Analysis",
    page_icon="📈",
    layout="wide",
)

load_css()

st.title("📈 Outlier & Distribution Analysis")
st.caption(
    "Identify unusual numerical values and understand their distributions "
    "before deeper customer, loan, and risk analysis."
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
        This page identifies unusually high or low numerical values in the
        Home Credit application portfolio.

        Outliers are investigated using statistical techniques such as the
        **Interquartile Range (IQR)** and percentile-based analysis.

        An extreme value is **not automatically treated as an error**.
        It may represent:

        - A genuine high-income customer
        - A genuinely large loan
        - An unusual but valid customer profile
        - A potential data-entry issue
        - A value requiring business-rule validation

        The objective is therefore to **identify and investigate outliers**
        rather than blindly remove them.
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
gender_sel = st.sidebar.selectbox("Gender", gender_options)

# Income group
income_group_options = ["All"] + sorted(
    df["INCOME_GROUP"].dropna().unique().tolist()
)
income_group_sel = st.sidebar.selectbox(
    "Income Group",
    income_group_options
)

# Age group
age_group_options = ["All"] + sorted(
    df["AGE_GROUP"].dropna().unique().tolist()
)
age_group_sel = st.sidebar.selectbox(
    "Age Group",
    age_group_options
)

# Contract type
contract_options = ["All"] + sorted(
    df["NAME_CONTRACT_TYPE"].dropna().unique().tolist()
)
contract_sel = st.sidebar.selectbox(
    "Contract Type",
    contract_options
)

# Default status
default_options = ["All", "Non-Default", "Default"]
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

if age_group_sel != "All":
    filtered = filtered[
        filtered["AGE_GROUP"] == age_group_sel
    ]

if contract_sel != "All":
    filtered = filtered[
        filtered["NAME_CONTRACT_TYPE"] == contract_sel
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
# OUTLIER FUNCTION
# ============================================================

def calculate_outliers(data, column):
    """
    Calculate IQR-based outliers for a numerical column.
    """

    values = data[column].dropna()

    if len(values) == 0:
        return {
            "Q1": np.nan,
            "Q3": np.nan,
            "IQR": np.nan,
            "Lower Bound": np.nan,
            "Upper Bound": np.nan,
            "Outlier Count": 0,
            "Outlier %": 0,
        }

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    outliers = values[
        (values < lower_bound) |
        (values > upper_bound)
    ]

    return {
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "Lower Bound": lower_bound,
        "Upper Bound": upper_bound,
        "Outlier Count": len(outliers),
        "Outlier %": (len(outliers) / len(values)) * 100,
    }


# ============================================================
# OUTLIER CALCULATIONS
# ============================================================

income_stats = calculate_outliers(
    filtered,
    "AMT_INCOME_TOTAL"
)

credit_stats = calculate_outliers(
    filtered,
    "AMT_CREDIT"
)

annuity_stats = calculate_outliers(
    filtered,
    "AMT_ANNUITY"
)

goods_stats = calculate_outliers(
    filtered,
    "AMT_GOODS_PRICE"
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Outlier Overview")

k1, k2, k3, k4 = st.columns(4)

with k1:
        numeric_column_count = filtered.select_dtypes(
    include=np.number
).shape[1]

kpi_card(
    "Numerical Columns",
    f"{numeric_column_count:,}"
)

with k2:
    variables_with_outliers = sum(
        stats["Outlier Count"] > 0
        for stats in [
            income_stats,
            credit_stats,
            annuity_stats,
            goods_stats,
            calculate_outliers(filtered, "DAYS_BIRTH"),
            calculate_outliers(filtered, "DAYS_EMPLOYED"),
            calculate_outliers(filtered, "CNT_CHILDREN"),
            calculate_outliers(filtered, "CNT_FAM_MEMBERS"),
        ]
    )

    kpi_card(
        "Variables with Outliers",
        str(variables_with_outliers)
    )

with k3:
    max_income = filtered["AMT_INCOME_TOTAL"].max()

    kpi_card(
        "Maximum Income",
        f"₹{max_income:,.0f}"
    )

with k4:
    max_credit = filtered["AMT_CREDIT"].max()

    kpi_card(
        "Maximum Credit",
        f"₹{max_credit:,.0f}"
    )


k5, k6, k7, k8 = st.columns(4)

with k5:
    kpi_card(
        "Maximum Annuity",
        f"₹{filtered['AMT_ANNUITY'].max():,.0f}"
    )

with k6:
    kpi_card(
        "Maximum Goods Price",
        f"₹{filtered['AMT_GOODS_PRICE'].max():,.0f}"
    )

with k7:
    kpi_card(
        "Income Outliers",
        f"{income_stats['Outlier Count']:,}"
    )

with k8:
    kpi_card(
        "Credit Outliers",
        f"{credit_stats['Outlier Count']:,}"
    )


st.divider()


# ============================================================
# DISTRIBUTION SECTION
# ============================================================

st.subheader("💰 Income Distribution")

income_plot_df = filtered[
    filtered["AMT_INCOME_TOTAL"].notna()
].copy()

# Use 99th percentile for visual readability only.
income_visual_limit = income_plot_df[
    "AMT_INCOME_TOTAL"
].quantile(0.99)

income_chart_df = income_plot_df[
    income_plot_df["AMT_INCOME_TOTAL"] <= income_visual_limit
]

fig = px.histogram(
    income_chart_df,
    x="AMT_INCOME_TOTAL",
    nbins=50,
    title="Income Distribution — Up to 99th Percentile",
    labels={
        "AMT_INCOME_TOTAL": "Annual Income"
    },
    color_discrete_sequence=[CHART_COLORS[0]],
)

fig.update_layout(
    template="plotly_white",
    margin=dict(t=50, l=10, r=10, b=10),
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.caption(
    f"Visualization capped at the 99th percentile "
    f"(₹{income_visual_limit:,.0f}) to make the main distribution easier to read. "
    "Outlier calculations use the complete dataset."
)


# ============================================================
# INCOME OUTLIERS
# ============================================================

st.subheader("📦 Income Outliers")

fig = px.box(
    filtered,
    y="AMT_INCOME_TOTAL",
    points="outliers",
    title="Income Outlier Detection using IQR",
    labels={
        "AMT_INCOME_TOTAL": "Annual Income"
    },
    color_discrete_sequence=[CHART_COLORS[1]],
)

fig.update_layout(
    template="plotly_white",
    margin=dict(t=50, l=10, r=10, b=10),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# CREDIT OUTLIERS
# ============================================================

st.subheader("💳 Credit Amount Outliers")

fig = px.box(
    filtered,
    y="AMT_CREDIT",
    points="outliers",
    title="Credit Amount Outlier Detection using IQR",
    labels={
        "AMT_CREDIT": "Credit Amount"
    },
    color_discrete_sequence=[CHART_COLORS[2]],
)

fig.update_layout(
    template="plotly_white",
    margin=dict(t=50, l=10, r=10, b=10),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# ANNUITY OUTLIERS
# ============================================================

st.subheader("💰 Annuity Outliers")

fig = px.box(
    filtered,
    y="AMT_ANNUITY",
    points="outliers",
    title="Annuity Outlier Detection using IQR",
    labels={
        "AMT_ANNUITY": "Annuity Amount"
    },
    color_discrete_sequence=[CHART_COLORS[3]],
)

fig.update_layout(
    template="plotly_white",
    margin=dict(t=50, l=10, r=10, b=10),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# INCOME VS CREDIT
# ============================================================

st.subheader("📈 Income vs Credit")

scatter_df = filtered[
    [
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "TARGET",
        "AGE_GROUP",
        "INCOME_GROUP",
    ]
].dropna()

# Limit displayed points for browser performance,
# while keeping the underlying calculations unchanged.
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
        "AGE_GROUP",
        "INCOME_GROUP",
    ],
    title="Relationship Between Customer Income and Credit Amount",
    labels={
        "AMT_INCOME_TOTAL": "Annual Income",
        "AMT_CREDIT": "Credit Amount",
        "TARGET": "Default Status",
    },
    color_discrete_sequence=CHART_COLORS,
    opacity=0.55,
)

fig.update_layout(
    template="plotly_white",
    margin=dict(t=50, l=10, r=10, b=10),
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# OUTLIER SUMMARY TABLE
# ============================================================

st.divider()

st.subheader("📋 Statistical Outlier Summary")

summary_rows = []

for column, label in [
    ("AMT_INCOME_TOTAL", "Income"),
    ("AMT_CREDIT", "Credit"),
    ("AMT_ANNUITY", "Annuity"),
    ("AMT_GOODS_PRICE", "Goods Price"),
    ("DAYS_BIRTH", "Days Birth"),
    ("DAYS_EMPLOYED", "Days Employed"),
    ("CNT_CHILDREN", "Children"),
    ("CNT_FAM_MEMBERS", "Family Members"),
]:

    stats = calculate_outliers(
        filtered,
        column
    )

    values = filtered[column].dropna()

    summary_rows.append(
        {
            "Variable": label,
            "Non-Missing Values": len(values),
            "Minimum": values.min() if len(values) else np.nan,
            "Median": values.median() if len(values) else np.nan,
            "Mean": values.mean() if len(values) else np.nan,
            "Maximum": values.max() if len(values) else np.nan,
            "Q1": stats["Q1"],
            "Q3": stats["Q3"],
            "IQR": stats["IQR"],
            "IQR Outliers": stats["Outlier Count"],
            "Outlier %": stats["Outlier %"],
        }
    )

outlier_summary = pd.DataFrame(summary_rows)

st.dataframe(
    outlier_summary.style.format(
        {
            "Minimum": "{:,.2f}",
            "Median": "{:,.2f}",
            "Mean": "{:,.2f}",
            "Maximum": "{:,.2f}",
            "Q1": "{:,.2f}",
            "Q3": "{:,.2f}",
            "IQR": "{:,.2f}",
            "Outlier %": "{:.2f}%",
        }
    ),
    use_container_width=True,
)


# ============================================================
# OUTLIER METHODOLOGY
# ============================================================

st.subheader("🧮 Outlier Detection Methodology")

st.markdown(
    """
### IQR Method

For each numerical variable:

**IQR = Q3 − Q1**

The standard statistical boundaries are:

- Lower Bound = Q1 − 1.5 × IQR
- Upper Bound = Q3 + 1.5 × IQR

Values outside these boundaries are flagged as statistical outliers.

### Other techniques to consider

**Percentile Capping**

Extreme values can be capped at selected percentiles when they
disproportionately affect analysis.

**Winsorization**

Extreme observations can be replaced with percentile boundary values
rather than removed.

**Log Transformation**

Highly right-skewed financial variables such as income and credit can
sometimes be analysed using a logarithmic transformation.

**Business-Rule Validation**

Statistical outliers should be checked against domain rules before any
cleaning decision is made.
"""
)


# ============================================================
# KEY OBSERVATIONS
# ============================================================

st.subheader("🔍 Key Observations")

income_outlier_pct = income_stats["Outlier %"]
credit_outlier_pct = credit_stats["Outlier %"]
annuity_outlier_pct = annuity_stats["Outlier %"]

st.markdown(
    f"""
- **Income:** {income_stats['Outlier Count']:,} records
  ({income_outlier_pct:.2f}%) are flagged as IQR outliers.
- **Credit:** {credit_stats['Outlier Count']:,} records
  ({credit_outlier_pct:.2f}%) are flagged as IQR outliers.
- **Annuity:** {annuity_stats['Outlier Count']:,} records
  ({annuity_outlier_pct:.2f}%) are flagged as IQR outliers.
- The maximum observed income is **₹{filtered['AMT_INCOME_TOTAL'].max():,.0f}**.
- The maximum observed credit amount is **₹{filtered['AMT_CREDIT'].max():,.0f}**.
- Outlier identification is statistical and **does not imply that the underlying
  customer record is incorrect**.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown(
    """
### 1. Financial variables require distribution-aware analysis

Income, credit and annuity amounts can contain substantial right-skew.
Median values and percentile-based statistics are therefore useful alongside
simple averages.

### 2. Extreme credit values should be investigated

Large credit amounts may represent legitimate high-value applications.
They should not automatically be removed from the portfolio.

### 3. Outliers can affect portfolio summaries

Extreme income and credit observations can materially influence averages,
correlations and scatter plots. Analysts should therefore compare results
with and without extreme observations where appropriate.

### 4. Statistical outliers are not necessarily data-quality errors

An IQR flag identifies an unusual observation relative to the distribution.
It does not prove that the record is invalid.

### 5. Outlier treatment should depend on analytical purpose

For reporting, legitimate extreme customers may need to remain in the
portfolio. For some statistical analyses, percentile capping or logarithmic
transformation may provide a more stable representation.
"""
)


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader("✅ Recommendations")

st.markdown(
    """
1. **Do not automatically delete financial outliers.**
   Validate extreme income, credit and annuity values against business rules.

2. **Use median and percentile statistics alongside mean values**
   when reporting highly skewed financial variables.

3. **Consider log transformation** for strongly right-skewed monetary
   variables when performing distribution-based analysis.

4. **Use percentile capping or winsorization selectively** when extreme
   observations distort a specific analytical technique.

5. **Maintain an outlier flag** so that unusual records can be investigated
   without permanently removing them from the source data.

6. **Compare default behaviour of extreme-value groups** in subsequent
   risk-analysis pages to determine whether unusual financial profiles
   correspond with different observed default rates.
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
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "AMT_GOODS_PRICE",
        "AGE_YEARS",
        "EMPLOYMENT_YEARS",
        "INCOME_GROUP",
        "AGE_GROUP",
        "EMPLOYMENT_GROUP",
    ]

    available_columns = [
        col for col in display_columns
        if col in filtered.columns
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
        file_name="outlier_analysis_filtered_data.csv",
        mime="text/csv",
    )