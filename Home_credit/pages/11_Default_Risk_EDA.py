import streamlit as st
import pandas as pd
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Default Risk EDA",
    page_icon="⚠️",
    layout="wide"
)

load_css()

st.title("⚠️ Default Risk EDA")
st.caption(
    "Explore observed default patterns across demographics, income, "
    "employment, education, occupation and contract type."
)


# ============================================================
# BUSINESS OBJECTIVE
# ============================================================

with st.expander("🎯 Business Objective", expanded=True):
    st.markdown("""
    This page performs descriptive EDA of the **TARGET** variable.

    The analysis compares default counts and observed default rates across
    customer demographics, income, employment, education, occupation and
    contract type.

    **Default Count** shows how many customers defaulted.

    **Default Rate** shows the percentage of customers within a group who
    defaulted.

    ⚠️ **This is descriptive EDA only. No predictive model is used.**
    """)


# ============================================================
# LOAD DATA
# ============================================================

df = load_data()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Filters")

filters = {
    "Gender": "CODE_GENDER",
    "Age Group": "AGE_GROUP",
    "Income Group": "INCOME_GROUP",
    "Education": "NAME_EDUCATION_TYPE",
    "Employment Group": "EMPLOYMENT_GROUP",
    "Contract Type": "NAME_CONTRACT_TYPE"
}

selected = {}

for label, column in filters.items():
    options = ["All"] + sorted(
        df[column].dropna().unique().tolist()
    )
    selected[column] = st.sidebar.selectbox(label, options)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df.copy()

for column, value in selected.items():
    if value != "All":
        filtered = filtered[filtered[column] == value]

if filtered.empty:
    st.warning("No customers match the selected filters.")
    st.stop()


# ============================================================
# BASIC METRICS
# ============================================================

total_customers = len(filtered)
default_customers = int((filtered["TARGET"] == 1).sum())
non_default_customers = int((filtered["TARGET"] == 0).sum())
default_rate = filtered["TARGET"].mean() * 100


# ============================================================
# REUSABLE DEFAULT-RATE FUNCTION
# ============================================================

def risk_summary(data, column):
    result = (
        data.groupby(column)["TARGET"]
        .agg(
            Customers="size",
            Defaults="sum",
            Default_Rate="mean"
        )
        .reset_index()
    )

    result["Default_Rate"] *= 100
    return result


def highest_risk_group(data, column):
    result = risk_summary(data, column)

    eligible = result[result["Customers"] >= 100]

    if not eligible.empty:
        result = eligible

    return (
        result.loc[result["Default_Rate"].idxmax(), column]
        if not result.empty
        else "N/A"
    )


def risk_chart(
    data,
    column,
    title,
    color,
    horizontal=False
):
    result = risk_summary(data, column)

    if horizontal:
        result = result.sort_values("Default_Rate")

        fig = px.bar(
            result,
            x="Default_Rate",
            y=column,
            orientation="h",
            text="Default_Rate",
            title=title,
            color_discrete_sequence=[color]
        )
    else:
        fig = px.bar(
            result,
            x=column,
            y="Default_Rate",
            text="Default_Rate",
            title=title,
            color_discrete_sequence=[color]
        )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        margin=dict(t=50, l=10, r=10, b=10)
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# HIGHEST-RISK GROUPS
# ============================================================

highest_risk_age = highest_risk_group(
    filtered,
    "AGE_GROUP"
)

highest_risk_income = highest_risk_group(
    filtered,
    "INCOME_GROUP"
)

highest_risk_employment = highest_risk_group(
    filtered,
    "EMPLOYMENT_GROUP"
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Default Risk Snapshot")

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    kpi_card(
        "Default Customers",
        f"{default_customers:,}"
    )

with c2:
    kpi_card(
        "Non-Default Customers",
        f"{non_default_customers:,}"
    )

with c3:
    kpi_card(
        "Observed Default Rate",
        f"{default_rate:.2f}%"
    )

with c4:
    kpi_card(
        "Highest-Risk Age",
        str(highest_risk_age)
    )

with c5:
    kpi_card(
        "Highest-Risk Income",
        str(highest_risk_income)
    )

with c6:
    kpi_card(
        "Highest-Risk Employment",
        str(highest_risk_employment)
    )


# ============================================================
# GRAPH 1 — DEFAULT VS NON-DEFAULT
# ============================================================

st.subheader("1️⃣ Default vs Non-Default Customers")

target_counts = (
    filtered["TARGET"]
    .value_counts()
    .reindex([0, 1], fill_value=0)
    .reset_index()
)

target_counts.columns = ["TARGET", "Customers"]

target_counts["Status"] = target_counts["TARGET"].map({
    0: "Non-Default",
    1: "Default"
})

fig = px.bar(
    target_counts,
    x="Status",
    y="Customers",
    text="Customers",
    title="Customer Distribution by Default Status",
    color="Status"
)

fig.update_traces(textposition="outside")
fig.update_layout(
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 2 — DEFAULT PERCENTAGE
# ============================================================

st.subheader("2️⃣ Default Percentage")

default_percentage = pd.DataFrame({
    "Status": ["Non-Default", "Default"],
    "Percentage": [
        non_default_customers / total_customers * 100,
        default_customers / total_customers * 100
    ]
})

fig = px.pie(
    default_percentage,
    values="Percentage",
    names="Status",
    hole=0.60,
    title="Observed Default Percentage",
    color_discrete_sequence=[
        CHART_COLORS[0],
        CHART_COLORS[2]
    ]
)

fig.update_traces(textinfo="percent+label")
fig.update_layout(template="plotly_white")

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 3 — AGE
# ============================================================

st.subheader("3️⃣ Default Rate by Age Group")

risk_chart(
    filtered,
    "AGE_GROUP",
    "Observed Default Rate by Age Group",
    CHART_COLORS[1]
)


# ============================================================
# GRAPH 4 — INCOME
# ============================================================

st.subheader("4️⃣ Default Rate by Income Group")

risk_chart(
    filtered,
    "INCOME_GROUP",
    "Observed Default Rate by Income Group",
    CHART_COLORS[2]
)


# ============================================================
# GRAPH 5 — EMPLOYMENT
# ============================================================

st.subheader("5️⃣ Default Rate by Employment Group")

risk_chart(
    filtered,
    "EMPLOYMENT_GROUP",
    "Observed Default Rate by Employment Group",
    CHART_COLORS[3],
    horizontal=True
)


# ============================================================
# GRAPH 6 — EDUCATION
# ============================================================

st.subheader("6️⃣ Default Rate by Education")

risk_chart(
    filtered,
    "NAME_EDUCATION_TYPE",
    "Observed Default Rate by Education",
    CHART_COLORS[0],
    horizontal=True
)


# ============================================================
# GRAPH 7 — OCCUPATION
# ============================================================

if "OCCUPATION_TYPE" in filtered.columns:

    st.subheader("7️⃣ Default Rate by Occupation")

    risk_chart(
        filtered,
        "OCCUPATION_TYPE",
        "Observed Default Rate by Occupation",
        CHART_COLORS[1],
        horizontal=True
    )


# ============================================================
# GRAPH 8 — CONTRACT TYPE
# ============================================================

st.subheader("8️⃣ Default Rate by Contract Type")

risk_chart(
    filtered,
    "NAME_CONTRACT_TYPE",
    "Observed Default Rate by Contract Type",
    CHART_COLORS[2]
)


# ============================================================
# SUMMARY TABLE
# ============================================================

st.divider()

st.subheader("📋 Default Risk Summary")

summary_columns = [
    "AGE_GROUP",
    "INCOME_GROUP",
    "EMPLOYMENT_GROUP",
    "NAME_EDUCATION_TYPE",
    "NAME_CONTRACT_TYPE"
]

if "OCCUPATION_TYPE" in filtered.columns:
    summary_columns.append("OCCUPATION_TYPE")

available = [
    c for c in summary_columns
    if c in filtered.columns
]

summary_frames = []

for column in available:

    temp = risk_summary(
        filtered,
        column
    )

    temp["Category"] = column

    temp = temp.rename(
        columns={column: "Group"}
    )

    summary_frames.append(
        temp[
            [
                "Category",
                "Group",
                "Customers",
                "Defaults",
                "Default_Rate"
            ]
        ]
    )

summary = pd.concat(
    summary_frames,
    ignore_index=True
)

st.dataframe(
    summary.style.format({
        "Customers": "{:,.0f}",
        "Defaults": "{:,.0f}",
        "Default_Rate": "{:.2f}%"
    }),
    use_container_width=True
)


# ============================================================
# KEY OBSERVATIONS
# ============================================================

st.subheader("🔍 Key Observations")

age_data = risk_summary(
    filtered,
    "AGE_GROUP"
)

income_data = risk_summary(
    filtered,
    "INCOME_GROUP"
)

employment_data = risk_summary(
    filtered,
    "EMPLOYMENT_GROUP"
)

age_max = age_data.loc[
    age_data["Default_Rate"].idxmax()
]

income_max = income_data.loc[
    income_data["Default_Rate"].idxmax()
]

employment_max = employment_data.loc[
    employment_data["Default_Rate"].idxmax()
]

st.markdown(
    f"""
- **{default_customers:,} customers** in the filtered portfolio are
  observed defaults, representing a default rate of **{default_rate:.2f}%**.
- The **{age_max['AGE_GROUP']}** age group has the highest observed
  default rate among age groups at **{age_max['Default_Rate']:.2f}%**.
- The **{income_max['INCOME_GROUP']}** income group has the highest
  observed default rate at **{income_max['Default_Rate']:.2f}%**.
- The **{employment_max['EMPLOYMENT_GROUP']}** employment group has the
  highest observed default rate at **{employment_max['Default_Rate']:.2f}%**.
- Default **rates** should be compared alongside customer counts because
  small groups can produce unstable percentages.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown("""
### 1. Default rates provide better group comparisons

Customer counts alone can be misleading because larger groups naturally
contain more defaults.

### 2. Demographic characteristics show different observed patterns

Age, income, employment and education groups can have different historical
default rates within the portfolio.

### 3. Employment stability can be monitored

Differences across employment groups may indicate different observed
repayment patterns.

### 4. Income segmentation adds affordability context

Comparing default rates across income groups helps identify differences
in observed portfolio behaviour.

### 5. Education and occupation provide additional segmentation

These characteristics can reveal differences in the composition of customers
with observed defaults.

### 6. Contract type can be compared separately

Different loan contract types may have different observed default rates.

### 7. Counts and rates should always be viewed together

A high default count does not necessarily mean that a group has the highest
risk rate.

### 8. These findings are descriptive

Observed relationships do not establish causation and should not be treated
as predictive rules.
""")


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.subheader("✅ Business Recommendations")

st.markdown("""
1. **Monitor groups with consistently higher observed default rates.**

2. **Compare default rates together with customer counts** before drawing
   conclusions about a segment.

3. **Track income and employment segments** as part of portfolio monitoring.

4. **Review demographic segments periodically** as portfolio composition
   changes.

5. **Use education and occupation as descriptive segmentation dimensions.**

6. **Compare contract types separately** when reviewing historical default
   patterns.

7. **Investigate unusually high default-rate groups** rather than assuming
   that every customer in the group is high risk.

8. **Avoid using a single demographic variable as a standalone decision rule.**

9. **Use Page 11 together with the affordability analysis on Page 10** for
   broader interpretation of customer financial behaviour.

10. **Use observed default patterns as EDA evidence, not as predictions.**
""")


# ============================================================
# FILTERED CUSTOMER TABLE
# ============================================================

st.divider()

with st.expander("📄 View Filtered Default-Risk Records"):

    display_columns = [
        "SK_ID_CURR",
        "TARGET",
        "CODE_GENDER",
        "AGE_GROUP",
        "INCOME_GROUP",
        "EMPLOYMENT_GROUP",
        "NAME_EDUCATION_TYPE",
        "OCCUPATION_TYPE",
        "NAME_CONTRACT_TYPE"
    ]

    display_columns = [
        c for c in display_columns
        if c in filtered.columns
    ]

    st.dataframe(
        filtered[display_columns].head(1000),
        use_container_width=True
    )

    csv = filtered[
        display_columns
    ].to_csv(index=False)

    st.download_button(
        "⬇️ Download Filtered Default-Risk Data",
        data=csv,
        file_name="default_risk_filtered_data.csv",
        mime="text/csv"
    )