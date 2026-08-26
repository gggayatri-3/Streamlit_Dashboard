import streamlit as st
import pandas as pd
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Customer Demographic Analysis",
    page_icon="👥",
    layout="wide",
)

load_css()

st.title("👥 Customer Demographic Analysis")
st.caption(
    "Understanding the demographic and household profile of Home Credit customers."
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
        This page analyses the demographic characteristics of Home Credit
        customers and identifies the typical customer profile.

        The analysis focuses on:

        - Age and age groups
        - Gender
        - Education
        - Family status
        - Income type
        - Household characteristics
        - Relationship between age and income

        The objective is to understand **who the customers are** and how
        demographic characteristics vary across the lending portfolio.
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


# Age Group
age_group_options = ["All"] + sorted(
    df["AGE_GROUP"].dropna().unique().tolist()
)

age_group_sel = st.sidebar.selectbox(
    "Age Group",
    age_group_options
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


if age_group_sel != "All":
    filtered = filtered[
        filtered["AGE_GROUP"] == age_group_sel
    ]


if income_group_sel != "All":
    filtered = filtered[
        filtered["INCOME_GROUP"] == income_group_sel
    ]


if education_sel != "All":
    filtered = filtered[
        filtered["NAME_EDUCATION_TYPE"] == education_sel
    ]


if family_status_sel != "All":
    filtered = filtered[
        filtered["NAME_FAMILY_STATUS"] == family_status_sel
    ]


if housing_sel != "All":
    filtered = filtered[
        filtered["NAME_HOUSING_TYPE"] == housing_sel
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

average_age = filtered["AGE_YEARS"].mean()
median_age = filtered["AGE_YEARS"].median()

most_common_gender = (
    filtered["CODE_GENDER"]
    .dropna()
    .mode()
)

most_common_gender = (
    most_common_gender.iloc[0]
    if not most_common_gender.empty
    else "N/A"
)


most_common_education = (
    filtered["NAME_EDUCATION_TYPE"]
    .dropna()
    .mode()
)

most_common_education = (
    most_common_education.iloc[0]
    if not most_common_education.empty
    else "N/A"
)


most_common_income_type = (
    filtered["NAME_INCOME_TYPE"]
    .dropna()
    .mode()
)

most_common_income_type = (
    most_common_income_type.iloc[0]
    if not most_common_income_type.empty
    else "N/A"
)


most_common_family_status = (
    filtered["NAME_FAMILY_STATUS"]
    .dropna()
    .mode()
)

most_common_family_status = (
    most_common_family_status.iloc[0]
    if not most_common_family_status.empty
    else "N/A"
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Customer Demographic Snapshot")

c1, c2, c3 = st.columns(3)

with c1:
    kpi_card(
        "Average Age",
        f"{average_age:.1f} years"
    )

with c2:
    kpi_card(
        "Median Age",
        f"{median_age:.1f} years"
    )

with c3:
    kpi_card(
        "Most Common Gender",
        str(most_common_gender)
    )


c4, c5, c6 = st.columns(3)

with c4:
    kpi_card(
        "Most Common Education",
        str(most_common_education)
    )

with c5:
    kpi_card(
        "Most Common Income Type",
        str(most_common_income_type)
    )

with c6:
    kpi_card(
        "Most Common Family Status",
        str(most_common_family_status)
    )


st.divider()


# ============================================================
# AGE DISTRIBUTION
# ============================================================

st.subheader("🎂 Age Distribution")

fig = px.histogram(
    filtered,
    x="AGE_YEARS",
    nbins=35,
    title="Customer Age Distribution",
    labels={
        "AGE_YEARS": "Age (Years)"
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
# GENDER DISTRIBUTION
# ============================================================

st.subheader("⚧ Gender Distribution")

gender_counts = (
    filtered["CODE_GENDER"]
    .value_counts()
    .reset_index()
)

gender_counts.columns = [
    "Gender",
    "Customers"
]

fig = px.pie(
    gender_counts,
    values="Customers",
    names="Gender",
    hole=0.55,
    title="Customer Distribution by Gender",
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
# EDUCATION DISTRIBUTION
# ============================================================

st.subheader("🎓 Education Distribution")

education_counts = (
    filtered["NAME_EDUCATION_TYPE"]
    .value_counts()
    .sort_values()
    .reset_index()
)

education_counts.columns = [
    "Education",
    "Customers"
]

fig = px.bar(
    education_counts,
    x="Customers",
    y="Education",
    orientation="h",
    title="Customers by Education Level",
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
# FAMILY STATUS
# ============================================================

st.subheader("👨‍👩‍👧 Family Status")

family_counts = (
    filtered["NAME_FAMILY_STATUS"]
    .value_counts()
    .reset_index()
)

family_counts.columns = [
    "Family Status",
    "Customers"
]

fig = px.bar(
    family_counts,
    x="Family Status",
    y="Customers",
    title="Customer Distribution by Family Status",
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
# INCOME TYPE
# ============================================================

st.subheader("💼 Income Type")

income_type_counts = (
    filtered["NAME_INCOME_TYPE"]
    .value_counts()
    .sort_values()
    .reset_index()
)

income_type_counts.columns = [
    "Income Type",
    "Customers"
]

fig = px.bar(
    income_type_counts,
    x="Customers",
    y="Income Type",
    orientation="h",
    title="Customers by Income Type",
    labels={
        "Customers": "Number of Customers"
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
# AGE GROUP BY GENDER
# ============================================================

st.subheader("👥 Age Group by Gender")

age_gender = (
    filtered.groupby(
        ["AGE_GROUP", "CODE_GENDER"]
    )
    .size()
    .reset_index(
        name="Customers"
    )
)

fig = px.bar(
    age_gender,
    x="AGE_GROUP",
    y="Customers",
    color="CODE_GENDER",
    barmode="group",
    title="Customer Age Groups by Gender",
    labels={
        "AGE_GROUP": "Age Group",
        "Customers": "Number of Customers",
        "CODE_GENDER": "Gender",
    },
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
# AGE VS INCOME
# ============================================================

st.subheader("📈 Age vs Income")

scatter_df = filtered[
    [
        "AGE_YEARS",
        "AMT_INCOME_TOTAL",
        "TARGET",
        "INCOME_GROUP",
        "NAME_EDUCATION_TYPE",
    ]
].dropna()


# Limit displayed points for browser performance.
# Underlying calculations still use all filtered records.
if len(scatter_df) > 15000:
    scatter_df = scatter_df.sample(
        15000,
        random_state=42
    )


fig = px.scatter(
    scatter_df,
    x="AGE_YEARS",
    y="AMT_INCOME_TOTAL",
    color="TARGET",
    hover_data=[
        "INCOME_GROUP",
        "NAME_EDUCATION_TYPE",
    ],
    title="Relationship Between Age and Customer Income",
    labels={
        "AGE_YEARS": "Age (Years)",
        "AMT_INCOME_TOTAL": "Annual Income",
        "TARGET": "Default Status",
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
# DEMOGRAPHIC SUMMARY TABLE
# ============================================================

st.divider()

st.subheader("📋 Demographic Summary")

summary_data = {
    "Metric": [
        "Customer Count",
        "Average Age",
        "Median Age",
        "Minimum Age",
        "Maximum Age",
        "Average Income",
        "Median Income",
        "Average Family Size",
        "Average Number of Children",
    ],
    "Value": [
        f"{len(filtered):,}",
        f"{filtered['AGE_YEARS'].mean():.1f}",
        f"{filtered['AGE_YEARS'].median():.1f}",
        f"{filtered['AGE_YEARS'].min():.1f}",
        f"{filtered['AGE_YEARS'].max():.1f}",
        f"₹{filtered['AMT_INCOME_TOTAL'].mean():,.0f}",
        f"₹{filtered['AMT_INCOME_TOTAL'].median():,.0f}",
        f"{filtered['CNT_FAM_MEMBERS'].mean():.2f}",
        f"{filtered['CNT_CHILDREN'].mean():.2f}",
    ],
}

summary_df = pd.DataFrame(summary_data)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# KEY OBSERVATIONS
# ============================================================

st.subheader("🔍 Key Observations")

age_group_counts = (
    filtered["AGE_GROUP"]
    .value_counts()
)

largest_age_group = (
    age_group_counts.index[0]
    if not age_group_counts.empty
    else "N/A"
)

largest_age_group_count = (
    age_group_counts.iloc[0]
    if not age_group_counts.empty
    else 0
)


education_counts_raw = (
    filtered["NAME_EDUCATION_TYPE"]
    .value_counts()
)

largest_education = (
    education_counts_raw.index[0]
    if not education_counts_raw.empty
    else "N/A"
)


income_counts_raw = (
    filtered["NAME_INCOME_TYPE"]
    .value_counts()
)

largest_income_type = (
    income_counts_raw.index[0]
    if not income_counts_raw.empty
    else "N/A"
)


st.markdown(
    f"""
- The average customer age is **{average_age:.1f} years**, while the median age is
  **{median_age:.1f} years**.
- The largest age segment is **{largest_age_group}**, containing approximately
  **{largest_age_group_count:,} customers**.
- The most common gender in the filtered portfolio is **{most_common_gender}**.
- **{largest_education}** is the most frequently observed education category.
- **{largest_income_type}** is the largest income-type segment.
- The average customer income is **₹{filtered['AMT_INCOME_TOTAL'].mean():,.0f}**,
  compared with a median income of **₹{filtered['AMT_INCOME_TOTAL'].median():,.0f}**.
- Differences between mean and median income can indicate that income is
  unevenly distributed across customers.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown(
    """
### 1. Customer composition matters

Understanding the dominant age, education, income and family-status groups
helps Home Credit understand the composition of its lending portfolio.

### 2. Age distribution provides portfolio context

Age groups can be compared with income, credit amounts and observed default
rates in subsequent analytical pages.

### 3. Income type provides an important customer dimension

Different income categories represent different employment and income
structures. Their portfolio sizes should therefore be considered when
interpreting later risk comparisons.

### 4. Education can provide additional segmentation context

Education levels may differ substantially in portfolio representation.
Observed differences should be treated as associations rather than causal
relationships.

### 5. Family characteristics help describe household structure

Family size and number of children provide useful context for later
affordability analysis, particularly when analysing income per family member.
"""
)


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader("✅ Recommendations")

st.markdown(
    """
1. **Monitor the largest demographic segments** because they represent the
   greatest share of the customer portfolio.

2. **Compare demographic groups with observed default rates** on the Default
   Risk EDA page rather than relying only on portfolio size.

3. **Use age groups as a standard dashboard filter** for deeper affordability
   and repayment analysis.

4. **Consider household structure when evaluating affordability**, especially
   where family size is large relative to household income.

5. **Track demographic portfolio composition over time** to identify changes
   in the customer base.

6. **Avoid interpreting demographic relationships as causal effects** without
   additional evidence.
"""
)


# ============================================================
# DETAILED FILTERED CUSTOMER DATA
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
        "NAME_EDUCATION_TYPE",
        "NAME_FAMILY_STATUS",
        "NAME_HOUSING_TYPE",
        "NAME_INCOME_TYPE",
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
        file_name="customer_demographics_filtered_data.csv",
        mime="text/csv",
    )