import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Executive Insights & Recommendations",
    page_icon="💡",
    layout="wide"
)

load_css()

# ============================================================
# LOAD DATA
# ============================================================

df = load_data()


# ============================================================
# HEADER
# ============================================================

st.title("💡 Executive Insights & Business Recommendations")

st.caption(
    "Management summary of portfolio patterns, affordability, "
    "repayment behaviour, observed default risk and business actions."
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Portfolio Filters")

gender_options = ["All"] + sorted(
    df["CODE_GENDER"].dropna().astype(str).unique().tolist()
)

gender_selected = st.sidebar.selectbox(
    "Gender",
    gender_options
)


age_options = ["All"] + sorted(
    df["AGE_GROUP"].dropna().astype(str).unique().tolist()
)

age_selected = st.sidebar.selectbox(
    "Age Group",
    age_options
)


income_options = ["All"] + sorted(
    df["INCOME_GROUP"].dropna().astype(str).unique().tolist()
)

income_selected = st.sidebar.selectbox(
    "Income Group",
    income_options
)


education_options = ["All"] + sorted(
    df["NAME_EDUCATION_TYPE"].dropna().astype(str).unique().tolist()
)

education_selected = st.sidebar.selectbox(
    "Education",
    education_options
)


contract_options = ["All"] + sorted(
    df["NAME_CONTRACT_TYPE"].dropna().astype(str).unique().tolist()
)

contract_selected = st.sidebar.selectbox(
    "Contract Type",
    contract_options
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df.copy()

if gender_selected != "All":
    filtered = filtered[
        filtered["CODE_GENDER"].astype(str) == gender_selected
    ]

if age_selected != "All":
    filtered = filtered[
        filtered["AGE_GROUP"].astype(str) == age_selected
    ]

if income_selected != "All":
    filtered = filtered[
        filtered["INCOME_GROUP"].astype(str) == income_selected
    ]

if education_selected != "All":
    filtered = filtered[
        filtered["NAME_EDUCATION_TYPE"].astype(str) == education_selected
    ]

if contract_selected != "All":
    filtered = filtered[
        filtered["NAME_CONTRACT_TYPE"].astype(str) == contract_selected
    ]


# ============================================================
# EMPTY FILTER CHECK
# ============================================================

if filtered.empty:

    st.warning(
        "No customers match the selected filters. "
        "Please broaden your filter selection."
    )

    st.stop()


# ============================================================
# BASIC METRICS
# ============================================================

total_customers = len(filtered)

default_customers = filtered["TARGET"].sum()

non_default_customers = (
    filtered["TARGET"] == 0
).sum()

default_rate = (
    filtered["TARGET"].mean() * 100
)

total_credit = filtered["AMT_CREDIT"].sum()

avg_credit = filtered["AMT_CREDIT"].mean()

avg_income = filtered["AMT_INCOME_TOTAL"].mean()

median_income = filtered["AMT_INCOME_TOTAL"].median()


# ============================================================
# AFFORDABILITY
# ============================================================

if "CREDIT_TO_INCOME" in filtered.columns:

    high_credit_burden = (
        filtered["CREDIT_TO_INCOME"] > 0.50
    ).sum()

else:

    high_credit_burden = 0


if "ANNUITY_TO_INCOME" in filtered.columns:

    high_annuity_burden = (
        filtered["ANNUITY_TO_INCOME"] > 0.30
    ).sum()

else:

    high_annuity_burden = 0


# ============================================================
# REPAYMENT
# ============================================================

if "LATE_PAYMENT_COUNT" in filtered.columns:

    late_payment_customers = (
        filtered["LATE_PAYMENT_COUNT"] > 0
    ).sum()

else:

    late_payment_customers = 0


# ============================================================
# BUREAU
# ============================================================

if "TOTAL_BUREAU_DEBT" in filtered.columns:

    bureau_debt_customers = (
        filtered["TOTAL_BUREAU_DEBT"] > 0
    ).sum()

else:

    bureau_debt_customers = 0


# ============================================================
# CREDIT CARD
# ============================================================

if "CREDIT_CARD_UTILIZATION" in filtered.columns:

    high_utilization_customers = (
        filtered["CREDIT_CARD_UTILIZATION"] > 0.70
    ).sum()

else:

    high_utilization_customers = 0


# ============================================================
# EXECUTIVE KPI ROW 1
# ============================================================

st.subheader("📌 Executive Portfolio Snapshot")

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    kpi_card(
        "Total Customers",
        f"{total_customers:,}"
    )

with c2:
    kpi_card(
        "Observed Default Rate",
        f"{default_rate:.1f}%"
    )

with c3:
    kpi_card(
        "Total Credit Exposure",
        f"₹{total_credit:,.0f}"
    )

with c4:
    kpi_card(
        "Average Credit",
        f"₹{avg_credit:,.0f}"
    )

with c5:
    kpi_card(
        "Average Income",
        f"₹{avg_income:,.0f}"
    )


# ============================================================
# EXECUTIVE KPI ROW 2
# ============================================================

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    kpi_card(
        "High-Burden Customers",
        f"{high_credit_burden:,}"
    )

with c2:
    kpi_card(
        "Late-Payment Customers",
        f"{late_payment_customers:,}"
    )

with c3:
    kpi_card(
        "Customers with Bureau Debt",
        f"{bureau_debt_customers:,}"
    )

with c4:
    kpi_card(
        "High Card Utilization",
        f"{high_utilization_customers:,}"
    )

with c5:
    kpi_card(
        "Default Customers",
        f"{default_customers:,}"
    )


st.divider()


# ============================================================
# PORTFOLIO OVERVIEW
# ============================================================

st.subheader("📊 Portfolio Overview")

col1, col2 = st.columns(2)


# Default distribution
with col1:

    default_data = pd.DataFrame({
        "Status": [
            "Non-Default",
            "Default"
        ],
        "Customers": [
            non_default_customers,
            default_customers
        ]
    })

    fig = px.bar(
        default_data,
        x="Status",
        y="Customers",
        title="Default vs Non-Default Customers",
        text="Customers",
        color_discrete_sequence=[CHART_COLORS[0]]
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


# Credit exposure
with col2:

    exposure = (
        filtered
        .groupby("INCOME_GROUP")["AMT_CREDIT"]
        .sum()
        .reset_index()
        .sort_values(
            "AMT_CREDIT",
            ascending=False
        )
    )

    fig = px.bar(
        exposure,
        x="INCOME_GROUP",
        y="AMT_CREDIT",
        title="Credit Exposure by Income Group",
        text_auto=".3s",
        color_discrete_sequence=[CHART_COLORS[1]]
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Income Group",
        yaxis_title="Total Credit"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# OBSERVED RISK PATTERNS
# ============================================================

st.subheader("⚠️ Observed Risk Patterns")

col1, col2 = st.columns(2)


# Income risk
with col1:

    income_risk = (
        filtered
        .groupby("INCOME_GROUP")["TARGET"]
        .mean()
        .mul(100)
        .reset_index(name="Default Rate")
        .sort_values(
            "Default Rate",
            ascending=False
        )
    )

    fig = px.bar(
        income_risk,
        x="INCOME_GROUP",
        y="Default Rate",
        title="Observed Default Rate by Income Group",
        text="Default Rate",
        color_discrete_sequence=[CHART_COLORS[2]]
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Observed Default Rate (%)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# Age risk
with col2:

    age_risk = (
        filtered
        .groupby("AGE_GROUP")["TARGET"]
        .mean()
        .mul(100)
        .reset_index(name="Default Rate")
    )

    fig = px.bar(
        age_risk,
        x="AGE_GROUP",
        y="Default Rate",
        title="Observed Default Rate by Age Group",
        text="Default Rate",
        color_discrete_sequence=[CHART_COLORS[3]]
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig.update_layout(
        template="plotly_white",
        yaxis_title="Observed Default Rate (%)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# AFFORDABILITY
# ============================================================

st.subheader("💰 Affordability & Financial Pressure")

col1, col2 = st.columns(2)


with col1:

    ratio_df = filtered[
        filtered["CREDIT_TO_INCOME"].notna()
    ].copy()

    ratio_df = ratio_df[
        ratio_df["CREDIT_TO_INCOME"]
        <
        ratio_df["CREDIT_TO_INCOME"].quantile(0.99)
    ]

    fig = px.histogram(
        ratio_df,
        x="CREDIT_TO_INCOME",
        nbins=40,
        title="Credit-to-Income Distribution",
        color_discrete_sequence=[CHART_COLORS[0]]
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Credit-to-Income Ratio",
        yaxis_title="Customers"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    ratio_df = filtered[
        filtered["ANNUITY_TO_INCOME"].notna()
    ].copy()

    ratio_df = ratio_df[
        ratio_df["ANNUITY_TO_INCOME"]
        <
        ratio_df["ANNUITY_TO_INCOME"].quantile(0.99)
    ]

    fig = px.histogram(
        ratio_df,
        x="ANNUITY_TO_INCOME",
        nbins=40,
        title="Annuity-to-Income Distribution",
        color_discrete_sequence=[CHART_COLORS[1]]
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Annuity-to-Income Ratio",
        yaxis_title="Customers"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# REPAYMENT & BUREAU
# ============================================================

st.subheader("💳 Repayment & Existing Credit Pressure")

col1, col2 = st.columns(2)


with col1:

    if "LATE_PAYMENT_COUNT" in filtered.columns:

        late_data = (
            filtered["LATE_PAYMENT_COUNT"]
            .fillna(0)
            .clip(upper=20)
        )

        fig = px.histogram(
            x=late_data,
            nbins=21,
            title="Late Payment Frequency",
            labels={
                "x": "Late Payment Count",
                "y": "Customers"
            },
            color_discrete_sequence=[CHART_COLORS[2]]
        )

        fig.update_layout(
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


with col2:

    if "TOTAL_BUREAU_DEBT" in filtered.columns:

        bureau_data = filtered[
            filtered["TOTAL_BUREAU_DEBT"] > 0
        ]["TOTAL_BUREAU_DEBT"]

        if len(bureau_data) > 0:

            bureau_data = bureau_data[
                bureau_data <
                bureau_data.quantile(0.99)
            ]

            fig = px.histogram(
                x=bureau_data,
                nbins=40,
                title="Existing Bureau Debt Distribution",
                labels={
                    "x": "Total Bureau Debt",
                    "y": "Customers"
                },
                color_discrete_sequence=[CHART_COLORS[3]]
            )

            fig.update_layout(
                template="plotly_white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# TOP 10 PORTFOLIO INSIGHTS
# ============================================================

st.divider()

st.subheader("🔍 Top 10 Portfolio Insights")

# Find largest income group
largest_income_group = (
    filtered["INCOME_GROUP"]
    .mode()
    .iloc[0]
)


# Highest income risk
income_risk_series = (
    filtered
    .groupby("INCOME_GROUP")["TARGET"]
    .mean()
    .dropna()
)

highest_income_risk = income_risk_series.idxmax()
highest_income_risk_rate = (
    income_risk_series.max() * 100
)


# Highest age risk
age_risk_series = (
    filtered
    .groupby("AGE_GROUP")["TARGET"]
    .mean()
    .dropna()
)

highest_age_risk = age_risk_series.idxmax()
highest_age_risk_rate = (
    age_risk_series.max() * 100
)


# Display insights using native Streamlit
insight_text = [

    (
        "Overall observed default",
        f"The current filtered portfolio has an observed default "
        f"rate of {default_rate:.1f}%."
    ),

    (
        "Portfolio exposure",
        f"Total current credit exposure is approximately "
        f"₹{total_credit:,.0f}."
    ),

    (
        "Largest customer segment",
        f"The most common income segment is "
        f"{largest_income_group}."
    ),

    (
        "Highest-risk income group",
        f"{highest_income_risk} has the highest observed default "
        f"rate at {highest_income_risk_rate:.1f}%."
    ),

    (
        "Highest-risk age group",
        f"{highest_age_risk} has the highest observed default "
        f"rate at {highest_age_risk_rate:.1f}%."
    ),

    (
        "Credit burden",
        f"{high_credit_burden:,} customers have a "
        f"credit-to-income ratio above 0.50."
    ),

    (
        "Annuity burden",
        f"{high_annuity_burden:,} customers have an "
        f"annuity-to-income ratio above 0.30."
    ),

    (
        "Repayment behaviour",
        f"{late_payment_customers:,} customers have at least "
        f"one recorded late installment payment."
    ),

    (
        "External credit pressure",
        f"{bureau_debt_customers:,} customers have recorded "
        f"bureau debt."
    ),

    (
        "Credit-card utilization",
        f"{high_utilization_customers:,} customers have "
        f"credit-card utilization above 70%."
    )
]


for number, (title, description) in enumerate(
    insight_text,
    start=1
):

    with st.container(border=True):

        st.markdown(
            f"### {number}. {title}"
        )

        st.write(description)


# ============================================================
# BUSINESS INTERPRETATION
# ============================================================

st.divider()

st.subheader("🧠 Business Interpretation")

st.markdown(
    f"""
**Affordability:**  
There are **{high_credit_burden:,} customers** with a
credit-to-income ratio above 0.50. This highlights a group with
relatively high current credit exposure compared with reported income.

**Repayment behaviour:**  
There are **{late_payment_customers:,} customers** with at least one
recorded late installment payment. Repeated delays can be useful for
ongoing repayment monitoring.

**External debt:**  
There are **{bureau_debt_customers:,} customers** with recorded bureau
debt. Existing external obligations should be considered together
with current credit exposure.

**Credit-card utilization:**  
There are **{high_utilization_customers:,} customers** with utilization
above 70% where credit-card information is available.

**Default interpretation:**  
Default counts should always be considered together with default rates.
A large customer segment can naturally contain more defaults simply
because it contains more customers.
"""
)


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.divider()

st.subheader("🎯 Business Recommendations")

recommendations = [

    (
        "Affordability Review",
        "Review applications with unusually high "
        "credit-to-income or annuity-to-income ratios."
    ),

    (
        "Monitor Repayment Delays",
        "Create periodic monitoring reports for customers "
        "showing repeated late installment payments."
    ),

    (
        "External Debt Monitoring",
        "Review customers with substantial bureau debt "
        "alongside their current Home Credit obligations."
    ),

    (
        "Credit Utilization Monitoring",
        "Monitor customers consistently using a large "
        "percentage of available credit-card limits."
    ),

    (
        "Income-Segment Monitoring",
        "Track observed default rates by income group while "
        "considering customer volume and credit exposure."
    ),

    (
        "Employment Stability",
        "Include employment duration and employment category "
        "in portfolio monitoring."
    ),

    (
        "Age-Based Monitoring",
        "Compare observed repayment and default patterns "
        "across customer age groups."
    ),

    (
        "High-Burden Customer Tracking",
        "Maintain a monitoring population for customers "
        "with elevated affordability ratios."
    ),

    (
        "Repeated Late-Payment Alerts",
        "Flag customers whose late-payment frequency "
        "increases over time."
    ),

    (
        "Bureau Overdue Monitoring",
        "Give additional attention to customers with "
        "overdue external credit balances."
    ),

    (
        "Portfolio Concentration",
        "Monitor credit exposure concentration across "
        "income, occupation and customer segments."
    ),

    (
        "Data Quality Improvement",
        "Improve collection and validation of important "
        "fields with substantial missing values."
    ),

    (
        "Risk Segment Monitoring",
        "Track movement between descriptive observed-risk "
        "segments as customer behaviour changes."
    ),

    (
        "Cross-Dataset Monitoring",
        "Combine application, bureau, previous application "
        "and repayment information for richer EDA."
    ),

    (
        "Management Reporting",
        "Use a recurring dashboard to monitor default rates, "
        "credit exposure, affordability and repayment patterns."
    )
]


for number, (title, recommendation) in enumerate(
    recommendations,
    start=1
):

    with st.container(border=True):

        st.markdown(
            f"### {number}. {title}"
        )

        st.write(recommendation)


# ============================================================
# FILTERED DATA TABLE
# ============================================================

st.divider()

st.subheader("📋 Portfolio Records Behind the Analysis")

display_columns = [
    col
    for col in [
        "SK_ID_CURR",
        "TARGET",
        "CODE_GENDER",
        "AGE_GROUP",
        "INCOME_GROUP",
        "NAME_EDUCATION_TYPE",
        "AMT_INCOME_TOTAL",
        "AMT_CREDIT",
        "AMT_ANNUITY",
        "CREDIT_TO_INCOME",
        "ANNUITY_TO_INCOME",
        "LATE_PAYMENT_COUNT",
        "TOTAL_BUREAU_DEBT",
        "CREDIT_CARD_UTILIZATION"
    ]
    if col in filtered.columns
]

st.dataframe(
    filtered[display_columns].head(1000),
    use_container_width=True,
    height=400
)


# ============================================================
# DOWNLOAD
# ============================================================

st.download_button(
    label="⬇️ Download Filtered Portfolio Data",
    data=filtered.to_csv(index=False),
    file_name="home_credit_filtered_executive_data.csv",
    mime="text/csv"
)


# ============================================================
# FINAL NOTE
# ============================================================

st.divider()

st.info(
    "All findings on this page are descriptive EDA observations. "
    "They are not predictive model outputs and should not be interpreted "
    "as causal relationships."
)