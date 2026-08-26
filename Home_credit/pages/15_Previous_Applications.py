import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Previous Applications",
    page_icon="📁",
    layout="wide"
)

load_css()

st.title("📁 Previous Application Analysis")
st.caption(
    "Analysis of customers' historical Home Credit loan applications, "
    "approval outcomes, contract types, products, and payment methods."
)

st.divider()


# ============================================================
# BUSINESS OBJECTIVE
# ============================================================

with st.expander("🎯 Business Objective", expanded=True):
    st.markdown(
        """
        This page analyses **previous Home Credit applications** to
        understand customers' historical borrowing behaviour.

        The analysis focuses on:

        - Previous application outcomes
        - Approved and refused applications
        - Contract types
        - Client types
        - Product types
        - Payment methods
        - Historical application and credit amounts
        - Customer-level application history

        The objective is to identify descriptive patterns in historical
        lending behaviour and understand how previous application history
        can provide context for current portfolio analysis.

        **Important:** This page is descriptive EDA and does not build a
        predictive model.
        """
    )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_previous_applications():

    possible_paths = [
        r"D:\Home_credit\data\raw\previous_application.csv",
        r"D:\Home_credit\raw_datasets\previous_application.csv",
        r"D:\Home_credit\previous_application.csv"
    ]

    for path in possible_paths:

        try:
            return pd.read_csv(path)

        except FileNotFoundError:
            continue

    raise FileNotFoundError(
        "previous_application.csv was not found. "
        "Please check the location of the file."
    )


df = load_previous_applications().copy()


# ============================================================
# NUMERIC CONVERSION
# ============================================================

numeric_columns = [
    "AMT_APPLICATION",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",
    "CNT_PAYMENT",
    "DAYS_DECISION",
    "HOUR_APPR_PROCESS_START"
]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# ============================================================
# STATUS CATEGORIES
# ============================================================

status_order = [
    "Approved",
    "Refused",
    "Cancelled",
    "Unused offer"
]


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Application Filters")


if "NAME_CONTRACT_TYPE" in df.columns:

    contract_options = ["All"] + sorted(
        df["NAME_CONTRACT_TYPE"]
        .dropna()
        .unique()
        .tolist()
    )

    contract_sel = st.sidebar.selectbox(
        "Contract Type",
        contract_options
    )

else:

    contract_sel = "All"


if "NAME_CONTRACT_STATUS" in df.columns:

    status_options = ["All"] + sorted(
        df["NAME_CONTRACT_STATUS"]
        .dropna()
        .unique()
        .tolist()
    )

    status_sel = st.sidebar.selectbox(
        "Application Status",
        status_options
    )

else:

    status_sel = "All"


if "NAME_CLIENT_TYPE" in df.columns:

    client_options = ["All"] + sorted(
        df["NAME_CLIENT_TYPE"]
        .dropna()
        .unique()
        .tolist()
    )

    client_sel = st.sidebar.selectbox(
        "Client Type",
        client_options
    )

else:

    client_sel = "All"


if "NAME_PRODUCT_TYPE" in df.columns:

    product_options = ["All"] + sorted(
        df["NAME_PRODUCT_TYPE"]
        .dropna()
        .unique()
        .tolist()
    )

    product_sel = st.sidebar.selectbox(
        "Product Type",
        product_options
    )

else:

    product_sel = "All"


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df.copy()


if contract_sel != "All":

    filtered = filtered[
        filtered["NAME_CONTRACT_TYPE"] == contract_sel
    ]


if status_sel != "All":

    filtered = filtered[
        filtered["NAME_CONTRACT_STATUS"] == status_sel
    ]


if client_sel != "All":

    filtered = filtered[
        filtered["NAME_CLIENT_TYPE"] == client_sel
    ]


if product_sel != "All":

    filtered = filtered[
        filtered["NAME_PRODUCT_TYPE"] == product_sel
    ]


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered.empty:

    st.warning(
        "No previous applications match the selected filters."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_applications = len(filtered)


approved_applications = (
    filtered["NAME_CONTRACT_STATUS"]
    .eq("Approved")
    .sum()
)


refused_applications = (
    filtered["NAME_CONTRACT_STATUS"]
    .eq("Refused")
    .sum()
)


cancelled_applications = (
    filtered["NAME_CONTRACT_STATUS"]
    .eq("Cancelled")
    .sum()
)


approval_rate = (
    approved_applications
    / total_applications
    * 100
    if total_applications > 0
    else 0
)


rejection_rate = (
    refused_applications
    / total_applications
    * 100
    if total_applications > 0
    else 0
)


avg_application = filtered[
    "AMT_APPLICATION"
].mean()


avg_credit = filtered[
    "AMT_CREDIT"
].mean()


avg_annuity = filtered[
    "AMT_ANNUITY"
].mean()


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Previous Application Portfolio")

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card(
        "Previous Applications",
        f"{total_applications:,}"
    )

with c2:
    kpi_card(
        "Approved Applications",
        f"{approved_applications:,}"
    )

with c3:
    kpi_card(
        "Refused Applications",
        f"{refused_applications:,}"
    )

with c4:
    kpi_card(
        "Cancelled Applications",
        f"{cancelled_applications:,}"
    )


c5, c6, c7, c8 = st.columns(4)

with c5:
    kpi_card(
        "Approval Rate",
        f"{approval_rate:.1f}%"
    )

with c6:
    kpi_card(
        "Rejection Rate",
        f"{rejection_rate:.1f}%"
    )

with c7:
    kpi_card(
        "Avg Previous Application",
        f"₹{avg_application:,.0f}"
    )

with c8:
    kpi_card(
        "Avg Previous Credit",
        f"₹{avg_credit:,.0f}"
    )


st.divider()


# ============================================================
# GRAPH 1 — APPLICATION STATUS
# ============================================================

st.subheader("1️⃣ Previous Application Status")

status_counts = (
    filtered["NAME_CONTRACT_STATUS"]
    .value_counts()
    .reset_index()
)

status_counts.columns = [
    "Status",
    "Applications"
]

fig = px.bar(
    status_counts.sort_values("Applications"),
    x="Applications",
    y="Status",
    orientation="h",
    text="Applications",
    title="Previous Applications by Contract Status",
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
# GRAPH 2 — APPROVAL PERCENTAGE
# ============================================================

st.subheader("2️⃣ Approval vs Other Outcomes")

approval_categories = pd.DataFrame({
    "Outcome": [
        "Approved",
        "Refused",
        "Cancelled",
        "Unused offer"
    ],
    "Applications": [
        (
            filtered["NAME_CONTRACT_STATUS"]
            == "Approved"
        ).sum(),

        (
            filtered["NAME_CONTRACT_STATUS"]
            == "Refused"
        ).sum(),

        (
            filtered["NAME_CONTRACT_STATUS"]
            == "Cancelled"
        ).sum(),

        (
            filtered["NAME_CONTRACT_STATUS"]
            == "Unused offer"
        ).sum()
    ]
})

approval_categories = approval_categories[
    approval_categories["Applications"] > 0
]


fig = px.pie(
    approval_categories,
    values="Applications",
    names="Outcome",
    hole=0.55,
    title="Previous Application Outcome Composition",
    color_discrete_sequence=CHART_COLORS
)

fig.update_traces(
    texttemplate="%{percent:.1%}",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "Applications: %{value:,}<br>"
        "Share: %{percent}<extra></extra>"
    )
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 3 — APPLICATION VS CREDIT
# ============================================================

st.subheader("3️⃣ Application Amount vs Credit Amount")

scatter_df = filtered[
    [
        "AMT_APPLICATION",
        "AMT_CREDIT",
        "NAME_CONTRACT_STATUS"
    ]
].dropna()


# Sampling keeps the chart responsive for the large dataset
if len(scatter_df) > 15000:

    scatter_df = scatter_df.sample(
        15000,
        random_state=42
    )


fig = px.scatter(
    scatter_df,
    x="AMT_APPLICATION",
    y="AMT_CREDIT",
    color="NAME_CONTRACT_STATUS",
    opacity=0.55,
    title="Requested Application Amount vs Granted Credit",
    labels={
        "AMT_APPLICATION": "Application Amount",
        "AMT_CREDIT": "Credit Amount",
        "NAME_CONTRACT_STATUS": "Status"
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
# GRAPH 4 — CONTRACT TYPES
# ============================================================

st.subheader("4️⃣ Previous Contract Types")

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
    text="Applications",
    title="Previous Applications by Contract Type",
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
# GRAPH 5 — CLIENT TYPE
# ============================================================

st.subheader("5️⃣ Client Type Distribution")

client_counts = (
    filtered["NAME_CLIENT_TYPE"]
    .value_counts()
    .reset_index()
)

client_counts.columns = [
    "Client Type",
    "Applications"
]

fig = px.bar(
    client_counts.sort_values("Applications"),
    x="Applications",
    y="Client Type",
    orientation="h",
    text="Applications",
    title="Previous Applications by Client Type",
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
# GRAPH 6 — PRODUCT TYPE
# ============================================================

st.subheader("6️⃣ Product Type Distribution")

product_counts = (
    filtered["NAME_PRODUCT_TYPE"]
    .value_counts()
    .reset_index()
)

product_counts.columns = [
    "Product Type",
    "Applications"
]

fig = px.bar(
    product_counts.sort_values("Applications"),
    x="Applications",
    y="Product Type",
    orientation="h",
    text="Applications",
    title="Previous Applications by Product Type",
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
# GRAPH 7 — PAYMENT TYPE
# ============================================================

st.subheader("7️⃣ Payment Type Distribution")

if "NAME_PAYMENT_TYPE" in filtered.columns:

    payment_counts = (
        filtered["NAME_PAYMENT_TYPE"]
        .value_counts()
        .reset_index()
    )

    payment_counts.columns = [
        "Payment Type",
        "Applications"
    ]

    fig = px.bar(
        payment_counts.sort_values(
            "Applications"
        ),
        x="Applications",
        y="Payment Type",
        orientation="h",
        text="Applications",
        title="Previous Applications by Payment Type",
        color_discrete_sequence=[
            CHART_COLORS[4]
            if len(CHART_COLORS) > 4
            else CHART_COLORS[0]
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
# GRAPH 8 — CREDIT AMOUNT DISTRIBUTION
# ============================================================

st.subheader("8️⃣ Previous Credit Amount Distribution")

credit_distribution = filtered[
    "AMT_CREDIT"
].dropna()


# Remove extreme values only for visualization
# using the 99th percentile.
if len(credit_distribution) > 0:

    credit_cap = credit_distribution.quantile(
        0.99
    )

    chart_credit = credit_distribution[
        credit_distribution <= credit_cap
    ]

    fig = px.histogram(
        chart_credit,
        x="AMT_CREDIT",
        nbins=50,
        title="Previous Credit Amount Distribution",
        color_discrete_sequence=[
            CHART_COLORS[0]
        ]
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Previous Credit Amount",
        yaxis_title="Applications"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# FEATURE ENGINEERING — CUSTOMER LEVEL
# ============================================================

st.divider()

st.subheader("👥 Customer-Level Previous Application Features")


customer_features = (
    filtered
    .groupby("SK_ID_CURR")
    .agg(
        PREVIOUS_APPLICATION_COUNT=(
            "SK_ID_PREV",
            "nunique"
        ),
        PREVIOUS_APPROVED_COUNT=(
            "NAME_CONTRACT_STATUS",
            lambda x: (
                x == "Approved"
            ).sum()
        ),
        PREVIOUS_REFUSED_COUNT=(
            "NAME_CONTRACT_STATUS",
            lambda x: (
                x == "Refused"
            ).sum()
        ),
        AVERAGE_PREVIOUS_CREDIT=(
            "AMT_CREDIT",
            "mean"
        ),
        MAXIMUM_PREVIOUS_CREDIT=(
            "AMT_CREDIT",
            "max"
        ),
        AVERAGE_APPLICATION_AMOUNT=(
            "AMT_APPLICATION",
            "mean"
        )
    )
    .reset_index()
)


customer_features[
    "PREVIOUS_APPROVAL_RATE"
] = (
    customer_features[
        "PREVIOUS_APPROVED_COUNT"
    ]
    / customer_features[
        "PREVIOUS_APPLICATION_COUNT"
    ]
    * 100
)


# ============================================================
# CUSTOMER KPI
# ============================================================

f1, f2, f3, f4 = st.columns(4)

with f1:

    kpi_card(
        "Customers with History",
        f"{len(customer_features):,}"
    )

with f2:

    kpi_card(
        "Avg Applications / Customer",
        f"{customer_features['PREVIOUS_APPLICATION_COUNT'].mean():.1f}"
    )

with f3:

    kpi_card(
        "Avg Customer Approval Rate",
        f"{customer_features['PREVIOUS_APPROVAL_RATE'].mean():.1f}%"
    )

with f4:

    kpi_card(
        "Max Previous Credit",
        f"₹{customer_features['MAXIMUM_PREVIOUS_CREDIT'].max():,.0f}"
    )


# ============================================================
# CUSTOMER APPLICATION HISTORY
# ============================================================

st.subheader(
    "📊 Previous Applications per Customer"
)

application_history = (
    customer_features[
        "PREVIOUS_APPLICATION_COUNT"
    ]
    .value_counts()
    .sort_index()
    .head(15)
    .reset_index()
)

application_history.columns = [
    "Previous Applications",
    "Customers"
]

fig = px.bar(
    application_history,
    x="Previous Applications",
    y="Customers",
    text="Customers",
    title="Customer Distribution by Number of Previous Applications",
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
# APPROVAL RATE BY CLIENT TYPE
# ============================================================

st.subheader(
    "📈 Approval Rate by Client Type"
)

client_approval = (
    filtered
    .groupby("NAME_CLIENT_TYPE")[
        "NAME_CONTRACT_STATUS"
    ]
    .apply(
        lambda x:
        (x == "Approved").mean() * 100
    )
    .sort_values()
    .reset_index()
)

client_approval.columns = [
    "Client Type",
    "Approval Rate"
]

fig = px.bar(
    client_approval,
    x="Approval Rate",
    y="Client Type",
    orientation="h",
    text="Approval Rate",
    title="Observed Approval Rate by Client Type",
    color_discrete_sequence=[
        CHART_COLORS[2]
    ]
)

fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    xaxis_title="Approval Rate (%)",
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# APPLICATION STATUS VS CREDIT
# ============================================================

st.subheader(
    "💰 Credit Amount by Application Outcome"
)

box_df = filtered[
    [
        "NAME_CONTRACT_STATUS",
        "AMT_CREDIT"
    ]
].dropna()


# Avoid extreme values dominating the visualization
if len(box_df) > 0:

    cap = box_df["AMT_CREDIT"].quantile(
        0.99
    )

    box_df = box_df[
        box_df["AMT_CREDIT"] <= cap
    ]

    fig = px.box(
        box_df,
        x="NAME_CONTRACT_STATUS",
        y="AMT_CREDIT",
        title="Previous Credit Amount by Application Outcome",
        color="NAME_CONTRACT_STATUS",
        color_discrete_sequence=CHART_COLORS
    )

    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        xaxis_title="Application Outcome",
        yaxis_title="Credit Amount"
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


most_common_status = (
    filtered["NAME_CONTRACT_STATUS"]
    .value_counts()
    .index[0]
)


most_common_contract = (
    filtered["NAME_CONTRACT_TYPE"]
    .value_counts()
    .index[0]
)


most_common_client = (
    filtered["NAME_CLIENT_TYPE"]
    .value_counts()
    .index[0]
)


most_common_product = (
    filtered["NAME_PRODUCT_TYPE"]
    .value_counts()
    .index[0]
)


st.markdown(
    f"""
- The filtered dataset contains **{total_applications:,} previous
  applications**.
- The most frequently observed application outcome is
  **{most_common_status}**.
- The most common historical contract type is
  **{most_common_contract}**.
- **{most_common_client}** is the largest client-type category.
- **{most_common_product}** is the most frequently observed product type.
- The observed approval rate in the current filter is
  **{approval_rate:.1f}%**.
- The observed refusal rate is
  **{rejection_rate:.1f}%**.
- The average previous credit amount is
  **₹{avg_credit:,.0f}**.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown(
    """
### 1. Previous application history reveals borrowing behaviour

Customers may have multiple historical applications, providing context
about their interaction with Home Credit.

### 2. Approval and refusal should be analysed separately

A high number of refusals does not automatically mean a customer group
has a high refusal tendency. Group size must also be considered.

### 3. Contract types represent different borrowing patterns

Different historical contract categories may have substantially different
application volumes.

### 4. Client type provides useful behavioural segmentation

New, repeater and other client categories can be compared to understand
how historical customers interact with the lending portfolio.

### 5. Product mix helps explain portfolio composition

Some product types may account for a large proportion of historical
applications and therefore deserve closer business monitoring.

### 6. Application amount and granted credit are not necessarily identical

Comparing requested application amounts with granted credit amounts can
highlight differences between requested and approved exposure.

### 7. Repeated applications provide additional customer context

Customers with several historical applications can be analysed separately
from customers with limited previous interaction.

### 8. Historical application behaviour should be combined with repayment data

Previous application outcomes alone do not describe repayment behaviour.
They should be interpreted together with installment, POS/CASH and
credit-card analysis.
"""
)


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.subheader("✅ Business Recommendations")

st.markdown(
    """
1. **Monitor customers with repeated previous applications** as a
   separate portfolio segment.

2. **Track approval and refusal rates by client type** rather than relying
   only on overall portfolio percentages.

3. **Review product categories with unusually high refusal rates** to
   understand potential portfolio-specific patterns.

4. **Compare requested application amounts with granted credit amounts**
   when analysing historical lending decisions.

5. **Monitor customers with extensive previous credit exposure** alongside
   their current credit-to-income ratio.

6. **Combine previous application history with bureau debt** to understand
   external and internal credit exposure together.

7. **Use previous approval history as descriptive context**, not as a
   prediction of future approval or default.

8. **Investigate repeated refused applications** through customer-level
   historical records.

9. **Compare client types with repayment behaviour** using the installment
   analysis from Page 17.

10. **Monitor product and contract concentration** to understand where the
    portfolio's historical lending activity is concentrated.

11. **Use customer-level previous application counts** in the descriptive
    risk segmentation on Page 19.

12. **Include historical application patterns in executive portfolio
    monitoring** on Page 20.
"""
)


# ============================================================
# CUSTOMER FEATURE TABLE
# ============================================================

st.divider()

with st.expander(
    "👥 View Customer-Level Previous Application Features"
):

    st.dataframe(
        customer_features.head(1000),
        use_container_width=True
    )


# ============================================================
# FILTERED DATA TABLE
# ============================================================

with st.expander(
    "📄 View Filtered Previous Application Records"
):

    st.dataframe(
        filtered.head(1000),
        use_container_width=True
    )


# ============================================================
# DOWNLOAD
# ============================================================

st.subheader("⬇️ Download Data")

filtered_csv = filtered.to_csv(
    index=False
)

st.download_button(
    label="Download Filtered Previous Applications",
    data=filtered_csv,
    file_name="filtered_previous_applications.csv",
    mime="text/csv"
)