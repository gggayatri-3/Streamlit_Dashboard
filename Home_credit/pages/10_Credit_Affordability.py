import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Credit Affordability Analysis",
    page_icon="💰",
    layout="wide"
)

load_css()

st.title("💰 Credit Affordability Analysis")
st.caption(
    "Explore income, loan exposure, repayment burden and observed "
    "default behaviour."
)

st.divider()


# ============================================================
# OBJECTIVE
# ============================================================

with st.expander("🎯 Business Objective", expanded=True):
    st.markdown("""
    This page evaluates observed affordability patterns using:

    - Credit-to-Income Ratio
    - Annuity-to-Income Ratio
    - Goods-to-Income Ratio
    - Credit-to-Goods Ratio
    - Income per Family Member
    - Observed default behaviour

    **Important:** These are descriptive EDA relationships, not causal
    conclusions or predictive model outputs.
    """)


# ============================================================
# LOAD DATA
# ============================================================

df = load_data().copy()


# ============================================================
# CREATE AFFORDABILITY FEATURES IF REQUIRED
# ============================================================

features = {
    "CREDIT_TO_INCOME": (
        "AMT_CREDIT", "AMT_INCOME_TOTAL"
    ),
    "ANNUITY_TO_INCOME": (
        "AMT_ANNUITY", "AMT_INCOME_TOTAL"
    ),
    "GOODS_TO_INCOME": (
        "AMT_GOODS_PRICE", "AMT_INCOME_TOTAL"
    ),
    "CREDIT_TO_GOODS": (
        "AMT_CREDIT", "AMT_GOODS_PRICE"
    ),
    "INCOME_PER_FAMILY_MEMBER": (
        "AMT_INCOME_TOTAL", "CNT_FAM_MEMBERS"
    )
}

for new_col, (num, den) in features.items():
    if new_col not in df.columns:
        df[new_col] = np.where(
            df[den] > 0,
            df[num] / df[den],
            np.nan
        )


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Filters")

filter_columns = {
    "Gender": "CODE_GENDER",
    "Age Group": "AGE_GROUP",
    "Income Group": "INCOME_GROUP",
    "Education": "NAME_EDUCATION_TYPE",
    "Employment Group": "EMPLOYMENT_GROUP",
    "Contract Type": "NAME_CONTRACT_TYPE"
}

selections = {}

for label, column in filter_columns.items():
    options = ["All"] + sorted(
        df[column].dropna().unique().tolist()
    )
    selections[column] = st.sidebar.selectbox(
        label,
        options
    )

default_sel = st.sidebar.selectbox(
    "Default Status",
    ["All", "Non-Default", "Default"]
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df.copy()

for column, value in selections.items():
    if value != "All":
        filtered = filtered[
            filtered[column] == value
        ]

if default_sel == "Default":
    filtered = filtered[filtered["TARGET"] == 1]

elif default_sel == "Non-Default":
    filtered = filtered[filtered["TARGET"] == 0]

if filtered.empty:
    st.warning("No customers match the selected filters.")
    st.stop()


# ============================================================
# CLEAN RATIO DATA
# ============================================================

ratio_cols = [
    "CREDIT_TO_INCOME",
    "ANNUITY_TO_INCOME",
    "GOODS_TO_INCOME",
    "CREDIT_TO_GOODS"
]

filtered[ratio_cols] = (
    filtered[ratio_cols]
    .apply(pd.to_numeric, errors="coerce")
)

filtered = filtered.replace(
    [np.inf, -np.inf],
    np.nan
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

avg_credit_income = filtered["CREDIT_TO_INCOME"].mean()
median_credit_income = filtered["CREDIT_TO_INCOME"].median()

avg_annuity_income = filtered["ANNUITY_TO_INCOME"].mean()

credit_threshold = filtered[
    "CREDIT_TO_INCOME"
].quantile(0.75)

annuity_threshold = filtered[
    "ANNUITY_TO_INCOME"
].quantile(0.75)

high_credit = (
    filtered["CREDIT_TO_INCOME"] > credit_threshold
).sum()

high_annuity = (
    filtered["ANNUITY_TO_INCOME"] > annuity_threshold
).sum()


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Affordability Snapshot")

kpis = [
    ("Avg Credit-to-Income", f"{avg_credit_income:.2f}x"),
    ("Median Credit-to-Income", f"{median_credit_income:.2f}x"),
    ("Avg Annuity-to-Income", f"{avg_annuity_income:.2%}"),
    ("High Credit Burden", f"{high_credit:,}"),
    ("High Annuity Burden", f"{high_annuity:,}")
]

cols = st.columns(5)

for col, (label, value) in zip(cols, kpis):
    with col:
        kpi_card(label, value)

st.caption(
    f"High burden = above the filtered portfolio's 75th percentile. "
    f"Credit threshold: {credit_threshold:.2f}x | "
    f"Annuity threshold: {annuity_threshold:.2%}"
)

st.divider()


# ============================================================
# HELPER FOR CHARTS
# ============================================================

def show_chart(fig):
    fig.update_layout(
        template="plotly_white",
        margin=dict(t=50, l=10, r=10, b=10)
    )
    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# 1. CREDIT-TO-INCOME DISTRIBUTION
# ============================================================

st.subheader("📈 Credit-to-Income Distribution")

plot = filtered["CREDIT_TO_INCOME"].dropna()
plot = plot[plot <= plot.quantile(.99)]

fig = px.histogram(
    plot,
    x="CREDIT_TO_INCOME",
    nbins=50,
    title="Credit-to-Income Ratio — Up to 99th Percentile",
    color_discrete_sequence=[CHART_COLORS[0]]
)

fig.add_vline(
    x=credit_threshold,
    line_dash="dash",
    annotation_text="75th Percentile"
)

show_chart(fig)


# ============================================================
# 2. ANNUITY-TO-INCOME DISTRIBUTION
# ============================================================

st.subheader("💵 Annuity-to-Income Distribution")

plot = filtered["ANNUITY_TO_INCOME"].dropna()
plot = plot[plot <= plot.quantile(.99)]

fig = px.histogram(
    plot,
    x="ANNUITY_TO_INCOME",
    nbins=50,
    title="Annuity-to-Income Ratio — Up to 99th Percentile",
    color_discrete_sequence=[CHART_COLORS[1]]
)

fig.add_vline(
    x=annuity_threshold,
    line_dash="dash",
    annotation_text="75th Percentile"
)

show_chart(fig)


# ============================================================
# 3. CREDIT-TO-INCOME BY DEFAULT
# ============================================================

st.subheader("⚠️ Credit-to-Income by Default Status")

plot = filtered[
    ["CREDIT_TO_INCOME", "TARGET"]
].dropna()

plot["Default Status"] = plot["TARGET"].map({
    0: "Non-Default",
    1: "Default"
})

limit = plot["CREDIT_TO_INCOME"].quantile(.99)
plot = plot[plot["CREDIT_TO_INCOME"] <= limit]

fig = px.box(
    plot,
    x="Default Status",
    y="CREDIT_TO_INCOME",
    color="Default Status",
    title="Credit-to-Income Ratio by Observed Default Status"
)

fig.update_layout(showlegend=False)

show_chart(fig)


# ============================================================
# 4. INCOME VS CREDIT
# ============================================================

st.subheader("💰 Income vs Credit")

plot = filtered[
    [
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "INCOME_GROUP"
    ]
].dropna()

income_limit = plot["AMT_INCOME_TOTAL"].quantile(.99)
credit_limit = plot["AMT_CREDIT"].quantile(.99)

plot = plot[
    (plot["AMT_INCOME_TOTAL"] <= income_limit) &
    (plot["AMT_CREDIT"] <= credit_limit)
]

fig = px.scatter(
    plot,
    x="AMT_INCOME_TOTAL",
    y="AMT_CREDIT",
    color="INCOME_GROUP",
    opacity=.5,
    title="Customer Income vs Credit Amount",
    labels={
        "AMT_INCOME_TOTAL": "Annual Income",
        "AMT_CREDIT": "Credit Amount"
    }
)

show_chart(fig)


# ============================================================
# 5. CREDIT BURDEN BY INCOME GROUP
# ============================================================

st.subheader("📊 Credit Burden by Income Group")

income_burden = (
    filtered
    .groupby("INCOME_GROUP")
    .agg(
        Average=("CREDIT_TO_INCOME", "mean"),
        Median=("CREDIT_TO_INCOME", "median"),
        Customers=("SK_ID_CURR", "count")
    )
    .reset_index()
)

fig = px.bar(
    income_burden,
    x="INCOME_GROUP",
    y="Average",
    text="Average",
    title="Average Credit-to-Income Ratio by Income Group",
    color_discrete_sequence=[CHART_COLORS[2]]
)

fig.update_traces(
    texttemplate="%{text:.2f}x",
    textposition="outside"
)

show_chart(fig)


# ============================================================
# 6. ANNUITY BURDEN BY AGE GROUP
# ============================================================

st.subheader("👥 Annuity Burden by Age Group")

age_burden = (
    filtered
    .groupby("AGE_GROUP")
    .agg(
        Average=("ANNUITY_TO_INCOME", "mean"),
        Median=("ANNUITY_TO_INCOME", "median"),
        Customers=("SK_ID_CURR", "count")
    )
    .reset_index()
)

fig = px.bar(
    age_burden,
    x="AGE_GROUP",
    y="Average",
    text="Average",
    title="Average Annuity-to-Income Ratio by Age Group",
    color_discrete_sequence=[CHART_COLORS[3]]
)

fig.update_traces(
    texttemplate="%{text:.2%}",
    textposition="outside"
)

show_chart(fig)


# ============================================================
# 7. GOODS-TO-INCOME
# ============================================================

st.subheader("🏷️ Goods-to-Income Ratio by Income Group")

goods = (
    filtered
    .groupby("INCOME_GROUP")["GOODS_TO_INCOME"]
    .mean()
    .sort_values()
    .reset_index()
)

fig = px.bar(
    goods,
    x="GOODS_TO_INCOME",
    y="INCOME_GROUP",
    orientation="h",
    text="GOODS_TO_INCOME",
    title="Average Goods-to-Income Ratio",
    color_discrete_sequence=[CHART_COLORS[0]]
)

fig.update_traces(
    texttemplate="%{text:.2f}x",
    textposition="outside"
)

show_chart(fig)


# ============================================================
# 8. CREDIT-TO-GOODS
# ============================================================

st.subheader("💳 Credit-to-Goods Ratio")

plot = filtered["CREDIT_TO_GOODS"].dropna()
plot = plot[plot <= plot.quantile(.99)]

fig = px.histogram(
    plot,
    x="CREDIT_TO_GOODS",
    nbins=50,
    title="Credit-to-Goods Ratio Distribution",
    color_discrete_sequence=[CHART_COLORS[1]]
)

show_chart(fig)


# ============================================================
# SUMMARY TABLE
# ============================================================

st.divider()

st.subheader("📋 Affordability Summary by Income Group")

summary = (
    filtered
    .groupby("INCOME_GROUP")
    .agg(
        Customers=("SK_ID_CURR", "count"),
        Average_Income=("AMT_INCOME_TOTAL", "mean"),
        Average_Credit=("AMT_CREDIT", "mean"),
        Average_Annuity=("AMT_ANNUITY", "mean"),
        Credit_to_Income=("CREDIT_TO_INCOME", "mean"),
        Median_Credit_to_Income=("CREDIT_TO_INCOME", "median"),
        Annuity_to_Income=("ANNUITY_TO_INCOME", "mean"),
        Goods_to_Income=("GOODS_TO_INCOME", "mean"),
        Default_Rate=("TARGET", "mean")
    )
    .reset_index()
)

summary["Default_Rate"] *= 100

st.dataframe(
    summary.style.format({
        "Customers": "{:,.0f}",
        "Average_Income": "₹{:,.0f}",
        "Average_Credit": "₹{:,.0f}",
        "Average_Annuity": "₹{:,.0f}",
        "Credit_to_Income": "{:.2f}x",
        "Median_Credit_to_Income": "{:.2f}x",
        "Annuity_to_Income": "{:.2%}",
        "Goods_to_Income": "{:.2f}x",
        "Default_Rate": "{:.2f}%"
    }),
    use_container_width=True
)


# ============================================================
# KEY OBSERVATIONS
# ============================================================

st.subheader("🔍 Key Observations")

highest_income_group = income_burden.loc[
    income_burden["Average"].idxmax(),
    "INCOME_GROUP"
]

highest_income_value = income_burden["Average"].max()

highest_age_group = age_burden.loc[
    age_burden["Average"].idxmax(),
    "AGE_GROUP"
]

highest_age_value = age_burden["Average"].max()

st.markdown(f"""
- Average Credit-to-Income is **{avg_credit_income:.2f}x**
  and median is **{median_credit_income:.2f}x**.
- **{highest_income_group}** has the highest average
  Credit-to-Income ratio at **{highest_income_value:.2f}x**.
- **{highest_age_group}** has the highest average
  Annuity-to-Income ratio at **{highest_age_value:.2%}**.
- **{high_credit:,} customers** are above the 75th-percentile
  Credit-to-Income level.
- **{high_annuity:,} customers** are above the 75th-percentile
  Annuity-to-Income level.
""")


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown("""
### 1. Credit burden should be viewed relative to income
Credit-to-Income provides more context than loan amount alone.

### 2. Mean and median should both be monitored
Large or unusual observations can influence average ratios.

### 3. Income groups can have different affordability profiles
Some income segments may carry relatively higher credit exposure.

### 4. Annuity burden provides complementary information
Customers with similar loan amounts may have different payment burdens.

### 5. Affordability and default can be compared
Differences are observed associations and should not be interpreted as causal.

### 6. Household structure matters
Income per family member adds another affordability perspective.
""")


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader("✅ Business Recommendations")

st.markdown("""
1. Monitor customers above the 75th-percentile Credit-to-Income level.
2. Monitor customers with high Annuity-to-Income ratios.
3. Compare affordability across income groups.
4. Use median ratios alongside averages.
5. Combine affordability with repayment behaviour from Page 17.
6. Compare affordability with bureau exposure from Page 13.
7. Monitor income-per-family-member differences.
8. Do not use one affordability ratio as a standalone risk rule.
9. Investigate extreme ratio observations individually.
10. Use affordability ratios for portfolio monitoring rather than prediction.
""")


# ============================================================
# FILTERED DATA
# ============================================================

st.divider()

with st.expander("📄 View Filtered Affordability Records"):

    columns = [
        "SK_ID_CURR",
        "TARGET",
        "CODE_GENDER",
        "AGE_GROUP",
        "INCOME_GROUP",
        "EMPLOYMENT_GROUP",
        "NAME_EDUCATION_TYPE",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "AMT_GOODS_PRICE",
        "CREDIT_TO_INCOME",
        "ANNUITY_TO_INCOME",
        "GOODS_TO_INCOME",
        "CREDIT_TO_GOODS",
        "INCOME_PER_FAMILY_MEMBER"
    ]

    columns = [
        c for c in columns
        if c in filtered.columns
    ]

    st.dataframe(
        filtered[columns].head(1000),
        use_container_width=True
    )

    st.download_button(
        "⬇️ Download Filtered Affordability Data",
        filtered[columns].to_csv(index=False),
        "credit_affordability_filtered_data.csv",
        "text/csv"
    )