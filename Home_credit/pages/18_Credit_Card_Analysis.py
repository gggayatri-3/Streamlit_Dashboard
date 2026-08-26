import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS
st.cache_data.clear()

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Credit Card Analysis",
    page_icon="💳",
    layout="wide"
)

load_css()

st.title("💳 Credit Card Balance Analysis")
st.caption(
    "Exploratory analysis of credit-card balances, credit limits, "
    "utilization, payments, drawings and delinquency behaviour."
)

st.divider()


# ============================================================
# BUSINESS OBJECTIVE
# ============================================================

with st.expander("🎯 Business Objective", expanded=True):
    st.markdown(
        """
        This page analyses historical credit-card behaviour using
        **credit_card_balance.csv**.

        The analysis focuses on:

        - Credit-card balances
        - Actual credit limits
        - Credit utilization
        - Drawings
        - Payments
        - Receivables
        - Days past due
        - Customer-level credit-card behaviour

        The objective is to identify descriptive patterns in credit-card
        usage and repayment behaviour.

        **Important:** These are observed historical patterns and should
        not be interpreted as predictions or causal relationships.
        """
    )


# ============================================================
# LOAD CREDIT CARD DATA
# ============================================================

@st.cache_data
def load_credit_card_data():

    possible_paths = [
        r"D:\Home_credit\data\raw\credit_card_balance.csv",
        r"D:\Home_credit\raw_datasets\credit_card_balance.csv",
        r"D:\Home_credit\credit_card_balance.csv"
    ]

    for path in possible_paths:

        try:
            return pd.read_csv(path)

        except FileNotFoundError:
            continue

    raise FileNotFoundError(
        "credit_card_balance.csv was not found. "
        "Please check that the file exists in your raw data folder."
    )

df = load_credit_card_data()


# ============================================================
# NUMERIC CONVERSION
# ============================================================

numeric_columns = [
    "AMT_BALANCE",
    "AMT_CREDIT_LIMIT_ACTUAL",
    "AMT_DRAWINGS_CURRENT",
    "AMT_PAYMENT_CURRENT",
    "AMT_TOTAL_RECEIVABLE",
    "CNT_DRAWINGS_CURRENT",
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
# FEATURE ENGINEERING
# ============================================================

# Credit Utilization
df["CREDIT_UTILIZATION"] = np.where(
    df["AMT_CREDIT_LIMIT_ACTUAL"] > 0,
    df["AMT_BALANCE"] /
    df["AMT_CREDIT_LIMIT_ACTUAL"],
    np.nan
)


# Payment-to-Balance Ratio
df["PAYMENT_TO_BALANCE"] = np.where(
    df["AMT_BALANCE"] > 0,
    df["AMT_PAYMENT_CURRENT"] /
    df["AMT_BALANCE"],
    np.nan
)


# Drawing-to-Credit-Limit Ratio
df["DRAWING_TO_LIMIT"] = np.where(
    df["AMT_CREDIT_LIMIT_ACTUAL"] > 0,
    df["AMT_DRAWINGS_CURRENT"] /
    df["AMT_CREDIT_LIMIT_ACTUAL"],
    np.nan
)


# DPD Flag
df["DPD_FLAG"] = (
    df["SK_DPD"].fillna(0) > 0
).astype(int)


# Default-style DPD flag
df["DPD_DEF_FLAG"] = (
    df["SK_DPD_DEF"].fillna(0) > 0
).astype(int)


# ============================================================
# UTILIZATION GROUPS
# ============================================================

def utilization_group(value):

    if pd.isna(value):
        return "Unknown"

    if value < 0.30:
        return "Low (<30%)"

    elif value < 0.50:
        return "Moderate (30–50%)"

    elif value < 0.75:
        return "High (50–75%)"

    elif value <= 1:
        return "Very High (75–100%)"

    else:
        return "Above Limit (>100%)"


df["UTILIZATION_GROUP"] = (
    df["CREDIT_UTILIZATION"]
    .apply(utilization_group)
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Credit Card Filters")


if "UTILIZATION_GROUP" in df.columns:

    utilization_options = [
        "All"
    ] + [
        x for x in [
            "Low (<30%)",
            "Moderate (30–50%)",
            "High (50–75%)",
            "Very High (75–100%)",
            "Above Limit (>100%)",
            "Unknown"
        ]
        if x in df["UTILIZATION_GROUP"].unique()
    ]

    utilization_sel = st.sidebar.selectbox(
        "Credit Utilization",
        utilization_options
    )

else:

    utilization_sel = "All"


dpd_filter = st.sidebar.selectbox(
    "DPD Status",
    [
        "All",
        "Customers with DPD",
        "No DPD"
    ]
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df.copy()


if utilization_sel != "All":

    filtered = filtered[
        filtered["UTILIZATION_GROUP"]
        == utilization_sel
    ]


if dpd_filter == "Customers with DPD":

    filtered = filtered[
        filtered["DPD_FLAG"] == 1
    ]

elif dpd_filter == "No DPD":

    filtered = filtered[
        filtered["DPD_FLAG"] == 0
    ]


# ============================================================
# EMPTY CHECK
# ============================================================

if filtered.empty:

    st.warning(
        "No credit-card records match the selected filters."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

credit_card_customers = (
    filtered["SK_ID_CURR"]
    .nunique()
)


average_balance = (
    filtered["AMT_BALANCE"]
    .mean()
)


average_limit = (
    filtered["AMT_CREDIT_LIMIT_ACTUAL"]
    .mean()
)


average_utilization = (
    filtered["CREDIT_UTILIZATION"]
    .mean()
    * 100
)


average_payment = (
    filtered["AMT_PAYMENT_CURRENT"]
    .mean()
)


customers_with_dpd = (
    filtered.loc[
        filtered["DPD_FLAG"] == 1,
        "SK_ID_CURR"
    ]
    .nunique()
)


average_drawings = (
    filtered["AMT_DRAWINGS_CURRENT"]
    .mean()
)


average_receivable = (
    filtered["AMT_TOTAL_RECEIVABLE"]
    .mean()
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Credit Card Portfolio Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:

    kpi_card(
        "Credit Card Customers",
        f"{credit_card_customers:,}"
    )

with c2:

    kpi_card(
        "Average Balance",
        f"₹{average_balance:,.0f}"
    )

with c3:

    kpi_card(
        "Average Credit Limit",
        f"₹{average_limit:,.0f}"
    )

with c4:

    kpi_card(
        "Average Utilization",
        f"{average_utilization:.1f}%"
    )


c5, c6, c7, c8 = st.columns(4)

with c5:

    kpi_card(
        "Average Monthly Payment",
        f"₹{average_payment:,.0f}"
    )

with c6:

    kpi_card(
        "Customers with DPD",
        f"{customers_with_dpd:,}"
    )

with c7:

    kpi_card(
        "Average Drawings",
        f"₹{average_drawings:,.0f}"
    )

with c8:

    kpi_card(
        "Average Receivable",
        f"₹{average_receivable:,.0f}"
    )


st.divider()


# ============================================================
# GRAPH 1 — CREDIT BALANCE DISTRIBUTION
# ============================================================

st.subheader("1️⃣ Credit Balance Distribution")

balance_data = (
    filtered["AMT_BALANCE"]
    .dropna()
)


if len(balance_data) > 0:

    upper = balance_data.quantile(0.99)

    balance_chart = balance_data[
        balance_data <= upper
    ]

    fig = px.histogram(
        balance_chart,
        x="AMT_BALANCE",
        nbins=60,
        title="Distribution of Credit Card Balances",
        color_discrete_sequence=[
            CHART_COLORS[0]
        ]
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Credit Card Balance",
        yaxis_title="Records"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# GRAPH 2 — CREDIT LIMIT DISTRIBUTION
# ============================================================

st.subheader("2️⃣ Credit Limit Distribution")

limit_data = (
    filtered["AMT_CREDIT_LIMIT_ACTUAL"]
    .dropna()
)


if len(limit_data) > 0:

    upper = limit_data.quantile(0.99)

    limit_chart = limit_data[
        limit_data <= upper
    ]

    fig = px.histogram(
        limit_chart,
        x="AMT_CREDIT_LIMIT_ACTUAL",
        nbins=50,
        title="Actual Credit Limit Distribution",
        color_discrete_sequence=[
            CHART_COLORS[1]
        ]
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Credit Limit",
        yaxis_title="Records"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# GRAPH 3 — CREDIT UTILIZATION DISTRIBUTION
# ============================================================

st.subheader("3️⃣ Credit Utilization Distribution")

util_data = (
    filtered["CREDIT_UTILIZATION"]
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
    .dropna()
)


if len(util_data) > 0:

    lower = util_data.quantile(0.01)
    upper = util_data.quantile(0.99)

    util_chart = util_data[
        (util_data >= lower)
        &
        (util_data <= upper)
    ]

    fig = px.histogram(
        util_chart,
        x="CREDIT_UTILIZATION",
        nbins=60,
        title="Credit Utilization Ratio",
        color_discrete_sequence=[
            CHART_COLORS[2]
        ]
    )

    fig.add_vline(
        x=0.30,
        line_dash="dash",
        annotation_text="30%"
    )

    fig.add_vline(
        x=0.75,
        line_dash="dash",
        annotation_text="75%"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Credit Utilization",
        yaxis_title="Records"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# GRAPH 4 — CREDIT LIMIT VS BALANCE
# ============================================================

st.subheader("4️⃣ Credit Limit vs Balance")

scatter_data = filtered[
    [
        "AMT_CREDIT_LIMIT_ACTUAL",
        "AMT_BALANCE",
        "UTILIZATION_GROUP"
    ]
].dropna()


if len(scatter_data) > 15000:

    scatter_data = scatter_data.sample(
        15000,
        random_state=42
    )


if len(scatter_data) > 0:

    limit_cap = scatter_data[
        "AMT_CREDIT_LIMIT_ACTUAL"
    ].quantile(0.99)

    balance_cap = scatter_data[
        "AMT_BALANCE"
    ].quantile(0.99)

    scatter_data = scatter_data[
        (scatter_data[
            "AMT_CREDIT_LIMIT_ACTUAL"
        ] <= limit_cap)
        &
        (scatter_data[
            "AMT_BALANCE"
        ] <= balance_cap)
    ]


fig = px.scatter(
    scatter_data,
    x="AMT_CREDIT_LIMIT_ACTUAL",
    y="AMT_BALANCE",
    color="UTILIZATION_GROUP",
    opacity=0.55,
    title="Credit Limit vs Credit Card Balance",
    labels={
        "AMT_CREDIT_LIMIT_ACTUAL":
            "Credit Limit",
        "AMT_BALANCE":
            "Balance",
        "UTILIZATION_GROUP":
            "Utilization Group"
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
# GRAPH 5 — BALANCE VS PAYMENT
# ============================================================

st.subheader("5️⃣ Balance vs Monthly Payment")

balance_payment = filtered[
    [
        "AMT_BALANCE",
        "AMT_PAYMENT_CURRENT"
    ]
].dropna()


if len(balance_payment) > 15000:

    balance_payment = balance_payment.sample(
        15000,
        random_state=42
    )


if len(balance_payment) > 0:

    balance_cap = balance_payment[
        "AMT_BALANCE"
    ].quantile(0.99)

    payment_cap = balance_payment[
        "AMT_PAYMENT_CURRENT"
    ].quantile(0.99)

    balance_payment = balance_payment[
        (balance_payment["AMT_BALANCE"] <= balance_cap)
        &
        (balance_payment["AMT_PAYMENT_CURRENT"] <= payment_cap)
    ]


fig = px.scatter(
    balance_payment,
    x="AMT_BALANCE",
    y="AMT_PAYMENT_CURRENT",
    opacity=0.5,
    title="Credit Card Balance vs Current Payment",
    labels={
        "AMT_BALANCE":
            "Credit Card Balance",
        "AMT_PAYMENT_CURRENT":
            "Current Payment"
    },
    color_discrete_sequence=[
        CHART_COLORS[3]
    ]
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 6 — DPD DISTRIBUTION
# ============================================================

st.subheader("6️⃣ Days Past Due Distribution")

dpd_data = (
    filtered["SK_DPD"]
    .dropna()
)


if len(dpd_data) > 0:

    upper = dpd_data.quantile(0.99)

    dpd_chart = dpd_data[
        dpd_data <= upper
    ]

    fig = px.histogram(
        dpd_chart,
        x="SK_DPD",
        nbins=50,
        title="Distribution of Days Past Due",
        color_discrete_sequence=[
            CHART_COLORS[4]
            if len(CHART_COLORS) > 4
            else CHART_COLORS[0]
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
# GRAPH 7 — UTILIZATION GROUP DISTRIBUTION
# ============================================================

st.subheader("7️⃣ Customers by Credit Utilization Group")

util_group = (
    filtered[
        "UTILIZATION_GROUP"
    ]
    .value_counts()
    .reindex(
        [
            "Low (<30%)",
            "Moderate (30–50%)",
            "High (50–75%)",
            "Very High (75–100%)",
            "Above Limit (>100%)",
            "Unknown"
        ],
        fill_value=0
    )
    .reset_index()
)

util_group.columns = [
    "Utilization Group",
    "Records"
]


fig = px.bar(
    util_group,
    x="Utilization Group",
    y="Records",
    text="Records",
    title="Credit Utilization Groups",
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
# GRAPH 8 — DPD BY UTILIZATION GROUP
# ============================================================

st.subheader(
    "8️⃣ DPD Behaviour Across Utilization Groups"
)

dpd_by_util = (
    filtered
    .groupby("UTILIZATION_GROUP")[
        "SK_DPD"
    ]
    .mean()
    .reindex(
        [
            "Low (<30%)",
            "Moderate (30–50%)",
            "High (50–75%)",
            "Very High (75–100%)",
            "Above Limit (>100%)",
            "Unknown"
        ]
    )
    .dropna()
    .reset_index()
)

dpd_by_util.columns = [
    "Utilization Group",
    "Average DPD"
]


fig = px.bar(
    dpd_by_util,
    x="Utilization Group",
    y="Average DPD",
    text="Average DPD",
    title="Average DPD by Credit Utilization Group",
    color_discrete_sequence=[
        CHART_COLORS[1]
    ]
)

fig.update_traces(
    texttemplate="%{y:.2f}",
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
# CUSTOMER-LEVEL FEATURES
# ============================================================

st.divider()

st.subheader(
    "👥 Customer-Level Credit Card Features"
)


customer_features = (
    filtered
    .groupby("SK_ID_CURR")
    .agg(
        AVERAGE_BALANCE=(
            "AMT_BALANCE",
            "mean"
        ),

        MAXIMUM_BALANCE=(
            "AMT_BALANCE",
            "max"
        ),

        AVERAGE_CREDIT_LIMIT=(
            "AMT_CREDIT_LIMIT_ACTUAL",
            "mean"
        ),

        AVERAGE_UTILIZATION=(
            "CREDIT_UTILIZATION",
            "mean"
        ),

        MAXIMUM_UTILIZATION=(
            "CREDIT_UTILIZATION",
            "max"
        ),

        TOTAL_DRAWINGS=(
            "AMT_DRAWINGS_CURRENT",
            "sum"
        ),

        AVERAGE_PAYMENTS=(
            "AMT_PAYMENT_CURRENT",
            "mean"
        ),

        MAXIMUM_DPD=(
            "SK_DPD",
            "max"
        ),

        RECORD_COUNT=(
            "SK_ID_PREV",
            "count"
        )
    )
    .reset_index()
)


# Convert utilization to percentage

customer_features[
    "AVERAGE_UTILIZATION_PCT"
] = (
    customer_features[
        "AVERAGE_UTILIZATION"
    ] * 100
)


customer_features[
    "MAXIMUM_UTILIZATION_PCT"
] = (
    customer_features[
        "MAXIMUM_UTILIZATION"
    ] * 100
)


# ============================================================
# CUSTOMER-LEVEL KPI
# ============================================================

f1, f2, f3, f4 = st.columns(4)

with f1:

    kpi_card(
        "Customers Analysed",
        f"{len(customer_features):,}"
    )

with f2:

    kpi_card(
        "Avg Customer Utilization",
        f"{customer_features['AVERAGE_UTILIZATION_PCT'].mean():.1f}%"
    )

with f3:

    kpi_card(
        "Avg Customer Balance",
        f"₹{customer_features['AVERAGE_BALANCE'].mean():,.0f}"
    )

with f4:

    kpi_card(
        "Maximum DPD",
        f"{customer_features['MAXIMUM_DPD'].max():,.0f} days"
    )


# ============================================================
# CUSTOMER UTILIZATION TABLE
# ============================================================

with st.expander(
    "👥 View Customer-Level Credit Card Features"
):

    st.dataframe(
        customer_features.head(1000),
        use_container_width=True
    )


# ============================================================
# KEY OBSERVATIONS
# ============================================================

st.divider()

st.subheader("🔍 Key Observations")


high_utilization_pct = (
    filtered[
        "CREDIT_UTILIZATION"
    ]
    .ge(0.75)
    .mean()
    * 100
)


dpd_record_pct = (
    filtered[
        "DPD_FLAG"
    ]
    .mean()
    * 100
)


st.markdown(
    f"""
- The filtered dataset contains **{len(filtered):,} credit-card
  records across {credit_card_customers:,} customers**.
- Average credit-card balance is approximately
  **₹{average_balance:,.0f}**.
- Average actual credit limit is approximately
  **₹{average_limit:,.0f}**.
- Average credit utilization is **{average_utilization:.1f}%**.
- Approximately **{high_utilization_pct:.1f}%** of records have credit
  utilization of **75% or higher**.
- Approximately **{dpd_record_pct:.1f}%** of credit-card records show
  at least one day past due.
- Average monthly payment is approximately
  **₹{average_payment:,.0f}**.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown(
    """
### 1. Credit utilization provides an important view of credit usage

Credit utilization compares the customer's outstanding balance with
their available credit limit.

### 2. High utilization should be interpreted as an observed usage pattern

Higher utilization indicates that a larger proportion of available credit
is being used. It should not automatically be labelled as default risk.

### 3. Balance and payment behaviour should be considered together

A high balance accompanied by substantial payments represents a different
pattern from a high balance accompanied by very small payments.

### 4. DPD provides a separate delinquency indicator

Days past due captures whether credit-card accounts have experienced
payment delinquency.

### 5. Repeated high utilization can indicate sustained credit usage

Customer-level aggregation helps distinguish temporary high utilization
from patterns observed across multiple historical records.

### 6. Credit-card behaviour should be combined with other Home Credit data

Credit-card utilization becomes more informative when viewed alongside
installment payment behaviour, bureau debt and previous applications.

### 7. Customer-level aggregation reduces the complexity of monthly records

The original credit-card table contains repeated historical observations.
Aggregated customer-level features provide a more useful portfolio view.

### 8. Correlation does not prove causation

Any relationship observed between utilization, balances, payments and
delinquency should be reported as an observed association rather than
a causal relationship.
"""
)


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.subheader("✅ Business Recommendations")

st.markdown(
    """
1. **Monitor customers with consistently high credit utilization.**

2. **Create periodic utilization reports** to identify changes in
   customer credit usage.

3. **Review customers showing both high utilization and DPD activity**
   as an observed financial-pressure pattern.

4. **Track maximum utilization as well as average utilization** because
   average values may hide short periods of unusually high usage.

5. **Monitor customers whose balances remain high across multiple
   historical periods.**

6. **Compare credit-card utilization with installment payment delays**
   when conducting descriptive customer reviews.

7. **Combine credit-card observations with bureau debt** to understand
   broader external credit exposure.

8. **Track customers with increasing DPD levels** for operational review.

9. **Use customer-level utilization features in Page 19's descriptive
   EDA risk segmentation.**

10. **Avoid treating high utilization alone as evidence of default.**

11. **Investigate unusually high utilization values** to distinguish
   genuine customer behaviour from potential data-quality issues.

12. **Monitor payment amounts alongside balances** rather than evaluating
   balance size in isolation.

13. **Use credit-card trends in portfolio monitoring dashboards** to
   identify changes in observed customer behaviour.

14. **Combine multiple independent repayment indicators** before making
   manual-review decisions.

15. **Include credit-card utilization and DPD features in the final
   executive recommendations on Page 20.**
"""
)


# ============================================================
# FILTERED DATA TABLE
# ============================================================

st.divider()

with st.expander(
    "📄 View Filtered Credit Card Records"
):

    st.dataframe(
        filtered.head(1000),
        use_container_width=True
    )


# ============================================================
# DOWNLOAD FILTERED DATA
# ============================================================

st.subheader("⬇️ Download Data")

filtered_csv = filtered.to_csv(
    index=False
)

st.download_button(
    label="Download Filtered Credit Card Data",
    data=filtered_csv,
    file_name="filtered_credit_card_balance.csv",
    mime="text/csv"
)


# ============================================================
# DOWNLOAD CUSTOMER FEATURES
# ============================================================

customer_csv = customer_features.to_csv(
    index=False
)

st.download_button(
    label="Download Customer-Level Credit Card Features",
    data=customer_csv,
    file_name="customer_credit_card_features.csv",
    mime="text/csv"
)