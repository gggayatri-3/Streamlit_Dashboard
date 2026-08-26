import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Installment Payment Analysis",
    page_icon="💰",
    layout="wide"
)

load_css()

st.title("💰 Installment Payment Analysis")
st.caption(
    "Detailed analysis of scheduled installments, actual payments, "
    "payment delays, underpayments, and repayment behaviour."
)

st.divider()


# ============================================================
# BUSINESS OBJECTIVE
# ============================================================

with st.expander("🎯 Business Objective", expanded=True):
    st.markdown(
        """
        This page analyses actual installment repayment behaviour using
        the **installments_payments.csv** dataset.

        The analysis focuses on:

        - Scheduled installment amounts
        - Actual payment amounts
        - Payment delays
        - Payment differences
        - Payment ratios
        - Early, on-time and late payments
        - Underpayments and overpayments
        - Customer-level repayment behaviour

        Repayment behaviour is particularly important because it provides
        descriptive evidence about how customers have historically managed
        their loan obligations.

        **Important:** This is exploratory and descriptive analysis only.
        No predictive model is developed.
        """
    )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_installments():

    possible_paths = [
        r"D:\Home_credit\data\raw\installments_payments.csv",
        r"D:\Home_credit\raw_datasets\installments_payments.csv",
        r"D:\Home_credit\installments_payments.csv"
    ]

    for path in possible_paths:

        try:
            return pd.read_csv(path)

        except FileNotFoundError:
            continue

    raise FileNotFoundError(
        "installments_payments.csv was not found. "
        "Please check the location of the file."
    )


df = load_installments().copy()


# ============================================================
# NUMERIC CONVERSION
# ============================================================

numeric_columns = [
    "NUM_INSTALMENT_VERSION",
    "NUM_INSTALMENT_NUMBER",
    "DAYS_INSTALMENT",
    "DAYS_ENTRY_PAYMENT",
    "AMT_INSTALMENT",
    "AMT_PAYMENT"
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

# Payment Delay
df["PAYMENT_DELAY"] = (
    df["DAYS_ENTRY_PAYMENT"]
    - df["DAYS_INSTALMENT"]
)


# Payment Difference
df["PAYMENT_DIFFERENCE"] = (
    df["AMT_PAYMENT"]
    - df["AMT_INSTALMENT"]
)


# Payment Ratio
df["PAYMENT_RATIO"] = np.where(
    df["AMT_INSTALMENT"] > 0,
    df["AMT_PAYMENT"] / df["AMT_INSTALMENT"],
    np.nan
)


# ============================================================
# PAYMENT TIMING CLASSIFICATION
# ============================================================

def classify_payment_delay(delay):

    if pd.isna(delay):
        return "Unknown"

    if delay < 0:
        return "Early Payment"

    elif delay == 0:
        return "On-Time Payment"

    else:
        return "Late Payment"


df["PAYMENT_TIMING"] = (
    df["PAYMENT_DELAY"]
    .apply(classify_payment_delay)
)


# ============================================================
# PAYMENT AMOUNT CLASSIFICATION
# ============================================================

def classify_payment_amount(row):

    installment = row["AMT_INSTALMENT"]
    payment = row["AMT_PAYMENT"]

    if pd.isna(installment) or pd.isna(payment):
        return "Unknown"

    if installment <= 0:
        return "Unknown"

    ratio = payment / installment

    if ratio < 0.999:
        return "Underpayment"

    elif ratio <= 1.001:
        return "Full Payment"

    else:
        return "Overpayment"


df["PAYMENT_AMOUNT_STATUS"] = (
    df.apply(
        classify_payment_amount,
        axis=1
    )
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Repayment Filters")


timing_options = [
    "All",
    "Early Payment",
    "On-Time Payment",
    "Late Payment",
    "Unknown"
]

timing_sel = st.sidebar.selectbox(
    "Payment Timing",
    timing_options
)


amount_options = [
    "All",
    "Underpayment",
    "Full Payment",
    "Overpayment",
    "Unknown"
]

amount_sel = st.sidebar.selectbox(
    "Payment Amount Status",
    amount_options
)


if "NUM_INSTALMENT_VERSION" in df.columns:

    version_options = ["All"] + sorted(
        df["NUM_INSTALMENT_VERSION"]
        .dropna()
        .unique()
        .tolist()
    )

    version_sel = st.sidebar.selectbox(
        "Installment Version",
        version_options
)

else:

    version_sel = "All"


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df.copy()


if timing_sel != "All":

    filtered = filtered[
        filtered["PAYMENT_TIMING"]
        == timing_sel
    ]


if amount_sel != "All":

    filtered = filtered[
        filtered["PAYMENT_AMOUNT_STATUS"]
        == amount_sel
    ]


if version_sel != "All":

    filtered = filtered[
        filtered["NUM_INSTALMENT_VERSION"]
        == version_sel
    ]


# ============================================================
# EMPTY CHECK
# ============================================================

if filtered.empty:

    st.warning(
        "No installment records match the selected filters."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_installments = len(filtered)


unique_customers = (
    filtered["SK_ID_CURR"]
    .nunique()
)


unique_previous_loans = (
    filtered["SK_ID_PREV"]
    .nunique()
)


average_installment = (
    filtered["AMT_INSTALMENT"]
    .mean()
)


average_payment = (
    filtered["AMT_PAYMENT"]
    .mean()
)


average_delay = (
    filtered["PAYMENT_DELAY"]
    .mean()
)


on_time_pct = (
    (
        filtered["PAYMENT_TIMING"]
        == "On-Time Payment"
    ).mean()
    * 100
)


late_pct = (
    (
        filtered["PAYMENT_TIMING"]
        == "Late Payment"
    ).mean()
    * 100
)


underpayment_pct = (
    (
        filtered["PAYMENT_AMOUNT_STATUS"]
        == "Underpayment"
    ).mean()
    * 100
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Repayment Portfolio Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card(
        "Total Installments",
        f"{total_installments:,}"
    )

with c2:
    kpi_card(
        "Unique Customers",
        f"{unique_customers:,}"
    )

with c3:
    kpi_card(
        "Average Installment",
        f"₹{average_installment:,.0f}"
    )

with c4:
    kpi_card(
        "Average Payment",
        f"₹{average_payment:,.0f}"
    )


c5, c6, c7, c8 = st.columns(4)

with c5:
    kpi_card(
        "On-Time Payment",
        f"{on_time_pct:.1f}%"
    )

with c6:
    kpi_card(
        "Late Payment",
        f"{late_pct:.1f}%"
    )

with c7:
    kpi_card(
        "Underpayment",
        f"{underpayment_pct:.1f}%"
    )

with c8:
    kpi_card(
        "Average Delay",
        f"{average_delay:.1f} days"
    )


st.divider()


# ============================================================
# GRAPH 1 — PAYMENT DELAY DISTRIBUTION
# ============================================================

st.subheader("1️⃣ Payment Delay Distribution")

delay_data = filtered[
    "PAYMENT_DELAY"
].dropna()


if len(delay_data) > 0:

    delay_cap_low = delay_data.quantile(0.01)
    delay_cap_high = delay_data.quantile(0.99)

    delay_chart = delay_data[
        (delay_data >= delay_cap_low)
        &
        (delay_data <= delay_cap_high)
    ]

    fig = px.histogram(
        delay_chart,
        x="PAYMENT_DELAY",
        nbins=60,
        title="Distribution of Payment Delay",
        color_discrete_sequence=[
            CHART_COLORS[0]
        ]
    )

    fig.add_vline(
        x=0,
        line_dash="dash",
        annotation_text="On-time"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Payment Delay (Days)",
        yaxis_title="Installments"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# GRAPH 2 — ON-TIME VS LATE
# ============================================================

st.subheader("2️⃣ Payment Timing Composition")

timing_counts = (
    filtered[
        "PAYMENT_TIMING"
    ]
    .value_counts()
    .reset_index()
)

timing_counts.columns = [
    "Payment Timing",
    "Installments"
]


fig = px.pie(
    timing_counts,
    values="Installments",
    names="Payment Timing",
    hole=0.55,
    title="Early, On-Time and Late Payments",
    color_discrete_sequence=CHART_COLORS
)

fig.update_traces(
    texttemplate="%{percent:.1%}"
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 3 — SCHEDULED VS ACTUAL PAYMENT
# ============================================================

st.subheader("3️⃣ Scheduled vs Actual Payment")

payment_scatter = filtered[
    [
        "AMT_INSTALMENT",
        "AMT_PAYMENT",
        "PAYMENT_TIMING"
    ]
].dropna()


if len(payment_scatter) > 15000:

    payment_scatter = payment_scatter.sample(
        15000,
        random_state=42
    )


# Limit extreme values only for visualization
if len(payment_scatter) > 0:

    x_cap = payment_scatter[
        "AMT_INSTALMENT"
    ].quantile(0.99)

    y_cap = payment_scatter[
        "AMT_PAYMENT"
    ].quantile(0.99)

    payment_scatter = payment_scatter[
        (payment_scatter["AMT_INSTALMENT"] <= x_cap)
        &
        (payment_scatter["AMT_PAYMENT"] <= y_cap)
    ]


fig = px.scatter(
    payment_scatter,
    x="AMT_INSTALMENT",
    y="AMT_PAYMENT",
    color="PAYMENT_TIMING",
    opacity=0.5,
    title="Scheduled Installment vs Actual Payment",
    labels={
        "AMT_INSTALMENT":
            "Scheduled Installment",
        "AMT_PAYMENT":
            "Actual Payment",
        "PAYMENT_TIMING":
            "Payment Timing"
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
# GRAPH 4 — PAYMENT DIFFERENCE
# ============================================================

st.subheader("4️⃣ Payment Difference Distribution")

difference_data = filtered[
    "PAYMENT_DIFFERENCE"
].dropna()


if len(difference_data) > 0:

    lower = difference_data.quantile(0.01)
    upper = difference_data.quantile(0.99)

    difference_chart = difference_data[
        (difference_data >= lower)
        &
        (difference_data <= upper)
    ]

    fig = px.histogram(
        difference_chart,
        x="PAYMENT_DIFFERENCE",
        nbins=60,
        title="Actual Payment minus Scheduled Installment",
        color_discrete_sequence=[
            CHART_COLORS[1]
        ]
    )

    fig.add_vline(
        x=0,
        line_dash="dash",
        annotation_text="Exact payment"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Payment Difference",
        yaxis_title="Installments"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# GRAPH 5 — PAYMENT AMOUNT STATUS
# ============================================================

st.subheader("5️⃣ Underpayment, Full Payment and Overpayment")

amount_status_counts = (
    filtered[
        "PAYMENT_AMOUNT_STATUS"
    ]
    .value_counts()
    .reset_index()
)

amount_status_counts.columns = [
    "Payment Status",
    "Installments"
]


fig = px.bar(
    amount_status_counts.sort_values(
        "Installments"
    ),
    x="Installments",
    y="Payment Status",
    orientation="h",
    text="Installments",
    title="Payment Amount Classification",
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
# GRAPH 6 — LATE PAYMENT COUNT BY CUSTOMER
# ============================================================

st.subheader("6️⃣ Late Payment Count by Customer")

late_customer = (
    filtered.assign(
        LATE_PAYMENT=
        (
            filtered["PAYMENT_TIMING"]
            == "Late Payment"
        ).astype(int)
    )
    .groupby("SK_ID_CURR")[
        "LATE_PAYMENT"
    ]
    .sum()
    .sort_values(
        ascending=False
    )
    .head(20)
    .reset_index()
)

late_customer.columns = [
    "Customer ID",
    "Late Payment Count"
]


fig = px.bar(
    late_customer.sort_values(
        "Late Payment Count"
    ),
    x="Late Payment Count",
    y="Customer ID",
    orientation="h",
    title="Top Customers by Late Payment Count",
    text="Late Payment Count",
    color_discrete_sequence=[
        CHART_COLORS[3]
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
# GRAPH 7 — DELAY VS PAYMENT AMOUNT
# ============================================================

st.subheader("7️⃣ Delay Days vs Payment Amount")

delay_payment = filtered[
    [
        "PAYMENT_DELAY",
        "AMT_PAYMENT",
        "PAYMENT_TIMING"
    ]
].dropna()


if len(delay_payment) > 15000:

    delay_payment = delay_payment.sample(
        15000,
        random_state=42
    )


if len(delay_payment) > 0:

    payment_cap = delay_payment[
        "AMT_PAYMENT"
    ].quantile(0.99)

    delay_payment = delay_payment[
        delay_payment["AMT_PAYMENT"]
        <= payment_cap
    ]


fig = px.scatter(
    delay_payment,
    x="PAYMENT_DELAY",
    y="AMT_PAYMENT",
    color="PAYMENT_TIMING",
    opacity=0.5,
    title="Payment Delay vs Actual Payment Amount",
    labels={
        "PAYMENT_DELAY":
            "Payment Delay (Days)",
        "AMT_PAYMENT":
            "Actual Payment",
        "PAYMENT_TIMING":
            "Payment Timing"
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
# GRAPH 8 — PAYMENT RATIO DISTRIBUTION
# ============================================================

st.subheader("8️⃣ Payment Ratio Distribution")

ratio_data = filtered[
    "PAYMENT_RATIO"
].replace(
    [np.inf, -np.inf],
    np.nan
).dropna()


if len(ratio_data) > 0:

    ratio_lower = ratio_data.quantile(0.01)
    ratio_upper = ratio_data.quantile(0.99)

    ratio_chart = ratio_data[
        (ratio_data >= ratio_lower)
        &
        (ratio_data <= ratio_upper)
    ]

    fig = px.histogram(
        ratio_chart,
        x="PAYMENT_RATIO",
        nbins=60,
        title="Actual Payment / Scheduled Installment",
        color_discrete_sequence=[
            CHART_COLORS[4]
            if len(CHART_COLORS) > 4
            else CHART_COLORS[0]
        ]
    )

    fig.add_vline(
        x=1,
        line_dash="dash",
        annotation_text="Full payment"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Payment Ratio",
        yaxis_title="Installments"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# CUSTOMER-LEVEL FEATURE ENGINEERING
# ============================================================

st.divider()

st.subheader(
    "👥 Customer-Level Repayment Features"
)


customer_features = (
    filtered
    .groupby("SK_ID_CURR")
    .agg(
        TOTAL_INSTALLMENTS=(
            "SK_ID_PREV",
            "count"
        ),

        LATE_PAYMENT_COUNT=(
            "PAYMENT_TIMING",
            lambda x:
            (x == "Late Payment").sum()
        ),

        EARLY_PAYMENT_COUNT=(
            "PAYMENT_TIMING",
            lambda x:
            (x == "Early Payment").sum()
        ),

        ON_TIME_PAYMENT_COUNT=(
            "PAYMENT_TIMING",
            lambda x:
            (x == "On-Time Payment").sum()
        ),

        UNDERPAYMENT_COUNT=(
            "PAYMENT_AMOUNT_STATUS",
            lambda x:
            (x == "Underpayment").sum()
        ),

        OVERPAYMENT_COUNT=(
            "PAYMENT_AMOUNT_STATUS",
            lambda x:
            (x == "Overpayment").sum()
        ),

        AVERAGE_PAYMENT_DELAY=(
            "PAYMENT_DELAY",
            "mean"
        ),

        MAXIMUM_PAYMENT_DELAY=(
            "PAYMENT_DELAY",
            "max"
        ),

        AVERAGE_PAYMENT_RATIO=(
            "PAYMENT_RATIO",
            "mean"
        )
    )
    .reset_index()
)


# ============================================================
# CUSTOMER-LEVEL DERIVED FEATURES
# ============================================================

customer_features[
    "LATE_PAYMENT_PERCENTAGE"
] = np.where(
    customer_features["TOTAL_INSTALLMENTS"] > 0,
    (
        customer_features[
            "LATE_PAYMENT_COUNT"
        ]
        /
        customer_features[
            "TOTAL_INSTALLMENTS"
        ]
        * 100
    ),
    0
)


# ============================================================
# CUSTOMER KPIs
# ============================================================

f1, f2, f3, f4 = st.columns(4)

with f1:

    kpi_card(
        "Customers Analysed",
        f"{len(customer_features):,}"
    )

with f2:

    kpi_card(
        "Avg Late Payments",
        f"{customer_features['LATE_PAYMENT_COUNT'].mean():.1f}"
    )

with f3:

    kpi_card(
        "Avg Late Payment %",
        f"{customer_features['LATE_PAYMENT_PERCENTAGE'].mean():.1f}%"
    )

with f4:

    kpi_card(
        "Max Payment Delay",
        f"{customer_features['MAXIMUM_PAYMENT_DELAY'].max():,.0f} days"
    )


# ============================================================
# CUSTOMER LATE PAYMENT DISTRIBUTION
# ============================================================

st.subheader(
    "📊 Distribution of Customer Late Payments"
)

late_distribution = (
    customer_features[
        "LATE_PAYMENT_COUNT"
    ]
    .value_counts()
    .sort_index()
    .head(20)
    .reset_index()
)

late_distribution.columns = [
    "Late Payment Count",
    "Customers"
]


fig = px.bar(
    late_distribution,
    x="Late Payment Count",
    y="Customers",
    text="Customers",
    title="Customers by Number of Late Payments",
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
# CUSTOMER PAYMENT DELAY
# ============================================================

st.subheader(
    "📈 Average Payment Delay by Customer"
)

customer_delay_chart = (
    customer_features[
        [
            "SK_ID_CURR",
            "AVERAGE_PAYMENT_DELAY"
        ]
    ]
    .dropna()
    .sort_values(
        "AVERAGE_PAYMENT_DELAY",
        ascending=False
    )
    .head(20)
)


fig = px.bar(
    customer_delay_chart.sort_values(
        "AVERAGE_PAYMENT_DELAY"
    ),
    x="AVERAGE_PAYMENT_DELAY",
    y="SK_ID_CURR",
    orientation="h",
    title="Customers with Highest Average Payment Delay",
    color_discrete_sequence=[
        CHART_COLORS[2]
    ]
)

fig.update_layout(
    template="plotly_white",
    showlegend=False,
    xaxis_title="Average Delay (Days)",
    yaxis_title="Customer ID"
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


timing_distribution = (
    filtered[
        "PAYMENT_TIMING"
    ]
    .value_counts(
        normalize=True
    )
    * 100
)


most_common_timing = (
    filtered[
        "PAYMENT_TIMING"
    ]
    .value_counts()
    .index[0]
)


most_common_amount_status = (
    filtered[
        "PAYMENT_AMOUNT_STATUS"
    ]
    .value_counts()
    .index[0]
)


st.markdown(
    f"""
- The filtered dataset contains **{total_installments:,} installment
  payment records** across **{unique_customers:,} customers**.
- The most common payment-timing category is
  **{most_common_timing}**.
- **{on_time_pct:.1f}%** of the filtered installment records are classified
  as on-time payments.
- **{late_pct:.1f}%** of the filtered installment records are classified
  as late payments.
- **{underpayment_pct:.1f}%** are classified as underpayments.
- The most common payment-amount classification is
  **{most_common_amount_status}**.
- The average scheduled installment is
  **₹{average_installment:,.0f}**.
- The average actual payment is
  **₹{average_payment:,.0f}**.
- The average observed payment delay is
  **{average_delay:.1f} days**.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown(
    """
### 1. Payment timing provides direct repayment evidence

The difference between scheduled and actual payment dates allows
installments to be classified as early, on-time or late.

### 2. Repeated late payments deserve more attention than isolated delays

A single late payment may represent an isolated event, while repeated
late payments can indicate a more persistent repayment pattern.

### 3. Payment amount and payment timing should be analysed together

A customer can pay late but eventually make the full payment, while
another customer may make an early but incomplete payment.

### 4. Underpayment provides a separate repayment signal

Comparing actual payment with the scheduled installment helps identify
installments where the customer paid less than the scheduled amount.

### 5. Payment ratio helps quantify repayment completeness

A ratio around 1 indicates that actual payment is approximately equal to
the scheduled installment.

### 6. Customer-level aggregation provides a clearer behavioural picture

Aggregating installment records by customer makes it possible to identify
customers with repeated delays, underpayments and unusually high average
payment delays.

### 7. Payment behaviour should be compared with other credit indicators

Installment behaviour should be interpreted together with bureau debt,
POS/CASH behaviour and credit-card utilization.

### 8. Observed repayment behaviour is not the same as predicted risk

These findings describe historical patterns in the dataset. They should
not be presented as predictions or causal conclusions.
"""
)


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.subheader("✅ Business Recommendations")

st.markdown(
    """
1. **Create early-warning monitoring for repeated late payments.**

2. **Track customers with increasing payment delays** across their
   installment history.

3. **Monitor customers with a high late-payment percentage** rather than
   relying only on total late-payment counts.

4. **Review repeated underpayment patterns** separately from late-payment
   patterns.

5. **Combine payment delay and payment ratio indicators** to understand
   repayment behaviour more completely.

6. **Prioritize customers with both repeated delays and underpayments**
   for manual account review.

7. **Compare installment behaviour with POS/CASH DPD indicators** to
   identify consistent delinquency patterns.

8. **Compare installment behaviour with bureau debt and overdue amounts**
   to understand broader financial exposure.

9. **Monitor customers whose maximum payment delay is unusually high.**

10. **Use customer-level repayment features in the descriptive risk
    segmentation on Page 19.**

11. **Track repayment-behaviour trends periodically** rather than
    evaluating customers using only one historical observation.

12. **Use repayment indicators in executive portfolio monitoring** on
    Page 20.

13. **Avoid treating a single late payment as definitive evidence of
    financial difficulty.**

14. **Investigate operational reasons for unusual payment patterns**
    before taking customer-level action.

15. **Build recurring repayment-behaviour reports** using the engineered
    customer-level features created on this page.
"""
)


# ============================================================
# CUSTOMER FEATURE TABLE
# ============================================================

st.divider()

with st.expander(
    "👥 View Customer-Level Repayment Features"
):

    st.dataframe(
        customer_features.head(1000),
        use_container_width=True
    )


# ============================================================
# FILTERED INSTALLMENT TABLE
# ============================================================

with st.expander(
    "📄 View Filtered Installment Records"
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
    label="Download Filtered Installment Data",
    data=filtered_csv,
    file_name="filtered_installment_payments.csv",
    mime="text/csv"
)


# ============================================================
# DOWNLOAD CUSTOMER FEATURES
# ============================================================

customer_csv = customer_features.to_csv(
    index=False
)

st.download_button(
    label="Download Customer Repayment Features",
    data=customer_csv,
    file_name="customer_repayment_features.csv",
    mime="text/csv"
)