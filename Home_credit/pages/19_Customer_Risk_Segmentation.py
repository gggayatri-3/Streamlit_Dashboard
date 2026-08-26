import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Customer Risk Segmentation",
    page_icon="🎯",
    layout="wide"
)

load_css()

st.title("🎯 Customer Risk Segmentation")
st.caption(
    "Descriptive customer segmentation based on observed affordability, "
    "employment, repayment and financial behaviour."
)

st.divider()


# ============================================================
# BUSINESS OBJECTIVE
# ============================================================

with st.expander("🎯 Business Objective", expanded=True):

    st.markdown(
        """
        This page creates **descriptive customer segments using
        EDA-driven business rules**.

        The segmentation considers observed characteristics such as:

        - Credit-to-income burden
        - Annuity-to-income burden
        - Employment stability
        - Income level
        - Family size
        - External credit indicators
        - Historical financial behaviour

        The resulting categories are:

        **Low Observed Risk**  
        **Moderate Observed Risk**  
        **Elevated Observed Risk**  
        **High Observed Risk**

        ⚠️ These are **descriptive EDA segments**, not predictions.
        No machine-learning model is used.
        """
    )


# ============================================================
# LOAD ENGINEERED APPLICATION DATA
# ============================================================

@st.cache_data
def load_application_data():

    possible_paths = [

        r"D:\Home_credit\processed_data\application_train_engineered_final.csv",

        r"D:\Home_credit\processed_data\application_train_engineered.csv",

        r"D:\Home_credit\data\processed\application_train_engineered.csv",

        r"D:\Home_credit\data\processed\application_train_engineered_final.csv",

    ]

    for path in possible_paths:

        try:

            return pd.read_csv(path)

        except FileNotFoundError:

            continue

    raise FileNotFoundError(
        "Engineered application dataset was not found."
    )


df = load_application_data().copy()


# ============================================================
# BASIC NUMERIC CONVERSION
# ============================================================

numeric_columns = [

    "TARGET",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AMT_GOODS_PRICE",
    "AGE_YEARS",
    "EMPLOYMENT_YEARS",
    "CREDIT_TO_INCOME",
    "ANNUITY_TO_INCOME",
    "GOODS_TO_INCOME",
    "CREDIT_TO_GOODS",
    "INCOME_PER_FAMILY_MEMBER"

]

for col in numeric_columns:

    if col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# ============================================================
# SAFE DEFAULT FEATURES
# ============================================================

# These features are optional because they may or may not
# already exist in the engineered dataset.

optional_features = {

    "BUREAU_ACCOUNT_COUNT": 0,
    "ACTIVE_BUREAU_COUNT": 0,
    "TOTAL_BUREAU_DEBT": 0,
    "TOTAL_BUREAU_OVERDUE": 0,

    "PREVIOUS_APPLICATION_COUNT": 0,
    "PREVIOUS_APPROVED_COUNT": 0,
    "AVERAGE_PREVIOUS_CREDIT": 0,
    "PREVIOUS_APPROVAL_RATE": 0,

    "TOTAL_INSTALLMENTS": 0,
    "LATE_PAYMENT_COUNT": 0,
    "AVERAGE_PAYMENT_DELAY": 0,
    "LATE_PAYMENT_PERCENTAGE": 0,

    "AVERAGE_CARD_BALANCE": 0,
    "AVERAGE_CREDIT_CARD_UTILIZATION": 0,
    "MAXIMUM_CREDIT_CARD_UTILIZATION": 0,
    "MAXIMUM_CARD_DPD": 0
}


for col, default_value in optional_features.items():

    if col not in df.columns:

        df[col] = default_value


# ============================================================
# CLEAN AGGREGATED FEATURES
# ============================================================

aggregate_features = list(
    optional_features.keys()
)

for col in aggregate_features:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

    df[col] = df[col].replace(
        [np.inf, -np.inf],
        np.nan
    )

    df[col] = df[col].fillna(0)


# ============================================================
# CREATE RULE FLAGS
# ============================================================

# ------------------------------------------------------------
# 1. HIGH CREDIT BURDEN
# ------------------------------------------------------------

credit_burden_threshold = (
    df["CREDIT_TO_INCOME"]
    .replace([np.inf, -np.inf], np.nan)
    .quantile(0.75)
)

df["HIGH_CREDIT_BURDEN"] = (

    df["CREDIT_TO_INCOME"]
    >= credit_burden_threshold

).astype(int)


# ------------------------------------------------------------
# 2. HIGH ANNUITY BURDEN
# ------------------------------------------------------------

annuity_burden_threshold = (
    df["ANNUITY_TO_INCOME"]
    .replace([np.inf, -np.inf], np.nan)
    .quantile(0.75)
)

df["HIGH_ANNUITY_BURDEN"] = (

    df["ANNUITY_TO_INCOME"]
    >= annuity_burden_threshold

).astype(int)


# ------------------------------------------------------------
# 3. SHORT EMPLOYMENT
# ------------------------------------------------------------

employment_threshold = 3

df["SHORT_EMPLOYMENT"] = (

    df["EMPLOYMENT_YEARS"]
    < employment_threshold

).astype(int)


# ------------------------------------------------------------
# 4. HIGH BUREAU DEBT
# ------------------------------------------------------------

bureau_debt_threshold = (

    df["TOTAL_BUREAU_DEBT"]
    .replace([np.inf, -np.inf], np.nan)
    .quantile(0.75)

)

df["HIGH_BUREAU_DEBT"] = (

    df["TOTAL_BUREAU_DEBT"]
    >= bureau_debt_threshold

).astype(int)


# ------------------------------------------------------------
# 5. HIGH BUREAU OVERDUE
# ------------------------------------------------------------

bureau_overdue_threshold = (

    df["TOTAL_BUREAU_OVERDUE"]
    .replace([np.inf, -np.inf], np.nan)
    .quantile(0.75)

)

df["HIGH_BUREAU_OVERDUE"] = (

    df["TOTAL_BUREAU_OVERDUE"]
    > bureau_overdue_threshold

).astype(int)


# ------------------------------------------------------------
# 6. REPEATED LATE PAYMENT
# ------------------------------------------------------------

df["REPEATED_LATE_PAYMENT"] = (

    df["LATE_PAYMENT_COUNT"]
    >= 3

).astype(int)


# ------------------------------------------------------------
# 7. HIGH CREDIT CARD UTILIZATION
# ------------------------------------------------------------

df["HIGH_CARD_UTILIZATION"] = (

    df["AVERAGE_CREDIT_CARD_UTILIZATION"]
    >= 0.75

).astype(int)


# ============================================================
# OBSERVED RISK SCORE
# ============================================================

risk_flags = [

    "HIGH_CREDIT_BURDEN",
    "HIGH_ANNUITY_BURDEN",
    "SHORT_EMPLOYMENT",
    "HIGH_BUREAU_DEBT",
    "HIGH_BUREAU_OVERDUE",
    "REPEATED_LATE_PAYMENT",
    "HIGH_CARD_UTILIZATION"

]

df["OBSERVED_RISK_SCORE"] = (

    df[risk_flags]
    .sum(axis=1)

)


# ============================================================
# DESCRIPTIVE RISK SEGMENT
# ============================================================

def assign_risk_segment(score):

    if score <= 1:

        return "Low Observed Risk"

    elif score <= 3:

        return "Moderate Observed Risk"

    elif score <= 5:

        return "Elevated Observed Risk"

    else:

        return "High Observed Risk"


df["RISK_SEGMENT"] = (

    df["OBSERVED_RISK_SCORE"]
    .apply(assign_risk_segment)

)


risk_order = [

    "Low Observed Risk",
    "Moderate Observed Risk",
    "Elevated Observed Risk",
    "High Observed Risk"

]


df["RISK_SEGMENT"] = pd.Categorical(

    df["RISK_SEGMENT"],

    categories=risk_order,

    ordered=True

)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Segmentation Filters")


gender_options = ["All"]

if "CODE_GENDER" in df.columns:

    gender_options += sorted(
        df["CODE_GENDER"]
        .dropna()
        .unique()
        .tolist()
    )


gender_sel = st.sidebar.selectbox(
    "Gender",
    gender_options
)


income_options = ["All"]

if "NAME_INCOME_TYPE" in df.columns:

    income_options += sorted(
        df["NAME_INCOME_TYPE"]
        .dropna()
        .unique()
        .tolist()
    )


income_sel = st.sidebar.selectbox(
    "Income Type",
    income_options
)


risk_sel = st.sidebar.selectbox(
    "Risk Segment",
    ["All"] + risk_order
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = df


if gender_sel != "All":

    filtered = filtered[
        filtered["CODE_GENDER"] == gender_sel
    ]


if income_sel != "All":

    filtered = filtered[
        filtered["NAME_INCOME_TYPE"] == income_sel
    ]


if risk_sel != "All":

    filtered = filtered[
        filtered["RISK_SEGMENT"] == risk_sel
    ]


if filtered.empty:

    st.warning(
        "No customers match the selected filters."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

low_count = (

    filtered[
        filtered["RISK_SEGMENT"]
        == "Low Observed Risk"
    ]["SK_ID_CURR"]
    .nunique()

)


moderate_count = (

    filtered[
        filtered["RISK_SEGMENT"]
        == "Moderate Observed Risk"
    ]["SK_ID_CURR"]
    .nunique()

)


elevated_count = (

    filtered[
        filtered["RISK_SEGMENT"]
        == "Elevated Observed Risk"
    ]["SK_ID_CURR"]
    .nunique()

)


high_count = (

    filtered[
        filtered["RISK_SEGMENT"]
        == "High Observed Risk"
    ]["SK_ID_CURR"]
    .nunique()

)


high_risk_exposure = (

    filtered[
        filtered["RISK_SEGMENT"]
        == "High Observed Risk"
    ]["AMT_CREDIT"]
    .sum()

)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Observed Risk Segment Overview")


c1, c2, c3, c4 = st.columns(4)


with c1:

    kpi_card(
        "Low-Risk Customers",
        f"{low_count:,}"
    )


with c2:

    kpi_card(
        "Moderate-Risk Customers",
        f"{moderate_count:,}"
    )


with c3:

    kpi_card(
        "Elevated-Risk Customers",
        f"{elevated_count:,}"
    )


with c4:

    kpi_card(
        "High-Risk Customers",
        f"{high_count:,}"
    )


c5, c6, c7, c8 = st.columns(4)


with c5:

    kpi_card(
        "High-Risk Credit Exposure",
        f"₹{high_risk_exposure:,.0f}"
    )


with c6:

    kpi_card(
        "Average Risk Score",
        f"{filtered['OBSERVED_RISK_SCORE'].mean():.2f}"
    )


with c7:

    kpi_card(
        "Customers Analysed",
        f"{filtered['SK_ID_CURR'].nunique():,}"
    )


with c8:

    kpi_card(
        "Observed Default Rate",
        f"{filtered['TARGET'].mean() * 100:.1f}%"
    )


st.divider()


# ============================================================
# GRAPH 1 — CUSTOMER COUNT
# ============================================================

st.subheader("1️⃣ Customer Count by Risk Segment")


segment_counts = (

    filtered
    .groupby(
        "RISK_SEGMENT",
        observed=False
    )["SK_ID_CURR"]
    .nunique()
    .reindex(
        risk_order,
        fill_value=0
    )
    .reset_index()

)


segment_counts.columns = [
    "Risk Segment",
    "Customers"
]


fig = px.bar(

    segment_counts,

    x="Risk Segment",

    y="Customers",

    text="Customers",

    title="Customers by Descriptive Risk Segment",

    color="Risk Segment",

    category_orders={
        "Risk Segment": risk_order
    },

    color_discrete_sequence=CHART_COLORS

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
# GRAPH 2 — PORTFOLIO EXPOSURE
# ============================================================

st.subheader("2️⃣ Portfolio Exposure by Risk Segment")


exposure = (

    filtered
    .groupby(
        "RISK_SEGMENT",
        observed=False
    )["AMT_CREDIT"]
    .sum()
    .reindex(
        risk_order,
        fill_value=0
    )
    .reset_index()

)


exposure.columns = [
    "Risk Segment",
    "Credit Exposure"
]


fig = px.pie(

    exposure,

    values="Credit Exposure",

    names="Risk Segment",

    hole=0.55,

    title="Credit Exposure Distribution",

    color="Risk Segment",

    color_discrete_sequence=CHART_COLORS

)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 3 — AVERAGE INCOME
# ============================================================

st.subheader("3️⃣ Average Income by Risk Segment")


income_segment = (

    filtered
    .groupby(
        "RISK_SEGMENT",
        observed=False
    )["AMT_INCOME_TOTAL"]
    .mean()
    .reindex(risk_order)
    .dropna()
    .reset_index()

)


income_segment.columns = [
    "Risk Segment",
    "Average Income"
]


fig = px.bar(

    income_segment,

    x="Risk Segment",

    y="Average Income",

    text="Average Income",

    title="Average Customer Income by Risk Segment",

    color="Risk Segment",

    category_orders={
        "Risk Segment": risk_order
    },

    color_discrete_sequence=CHART_COLORS

)


fig.update_traces(

    texttemplate="₹%{y:,.0f}",

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
# GRAPH 4 — AVERAGE CREDIT
# ============================================================

st.subheader("4️⃣ Average Credit by Risk Segment")


credit_segment = (

    filtered
    .groupby(
        "RISK_SEGMENT",
        observed=False
    )["AMT_CREDIT"]
    .mean()
    .reindex(risk_order)
    .dropna()
    .reset_index()

)


credit_segment.columns = [
    "Risk Segment",
    "Average Credit"
]


fig = px.bar(

    credit_segment,

    x="Risk Segment",

    y="Average Credit",

    text="Average Credit",

    title="Average Credit Amount by Risk Segment",

    color="Risk Segment",

    category_orders={
        "Risk Segment": risk_order
    },

    color_discrete_sequence=CHART_COLORS

)


fig.update_traces(

    texttemplate="₹%{y:,.0f}",

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
# GRAPH 5 — CREDIT TO INCOME
# ============================================================

st.subheader(
    "5️⃣ Credit-to-Income Ratio by Risk Segment"
)


ratio_data = filtered[
    [
        "RISK_SEGMENT",
        "CREDIT_TO_INCOME"
    ]
].dropna()


fig = px.box(

    ratio_data,

    x="RISK_SEGMENT",

    y="CREDIT_TO_INCOME",

    category_orders={
        "RISK_SEGMENT": risk_order
    },

    title="Credit-to-Income Ratio Across Risk Segments",

    color="RISK_SEGMENT",

    color_discrete_sequence=CHART_COLORS

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
# GRAPH 6 — LATE PAYMENTS
# ============================================================

st.subheader(
    "6️⃣ Late Payments by Risk Segment"
)


late_segment = (

    filtered
    .groupby(
        "RISK_SEGMENT",
        observed=False
    )["LATE_PAYMENT_COUNT"]
    .mean()
    .reindex(risk_order)
    .fillna(0)
    .reset_index()

)


late_segment.columns = [
    "Risk Segment",
    "Average Late Payments"
]


fig = px.bar(

    late_segment,

    x="Risk Segment",

    y="Average Late Payments",

    text="Average Late Payments",

    title="Average Late Payment Count by Risk Segment",

    color="Risk Segment",

    category_orders={
        "Risk Segment": risk_order
    },

    color_discrete_sequence=CHART_COLORS

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
# GRAPH 7 — BUREAU DEBT
# ============================================================

st.subheader(
    "7️⃣ Bureau Debt by Risk Segment"
)


bureau_segment = (

    filtered
    .groupby(
        "RISK_SEGMENT",
        observed=False
    )["TOTAL_BUREAU_DEBT"]
    .mean()
    .reindex(risk_order)
    .fillna(0)
    .reset_index()

)


bureau_segment.columns = [
    "Risk Segment",
    "Average Bureau Debt"
]


fig = px.bar(

    bureau_segment,

    x="Risk Segment",

    y="Average Bureau Debt",

    text="Average Bureau Debt",

    title="Average Bureau Debt by Risk Segment",

    color="Risk Segment",

    category_orders={
        "Risk Segment": risk_order
    },

    color_discrete_sequence=CHART_COLORS

)


fig.update_traces(

    texttemplate="₹%{y:,.0f}",

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
# GRAPH 8 — DEFAULT RATE
# ============================================================

st.subheader(
    "8️⃣ Observed Default Rate by Risk Segment"
)


default_segment = (

    filtered
    .groupby(
        "RISK_SEGMENT",
        observed=False
    )["TARGET"]
    .mean()
    .mul(100)
    .reindex(risk_order)
    .dropna()
    .reset_index()

)


default_segment.columns = [
    "Risk Segment",
    "Default Rate"
]


fig = px.bar(

    default_segment,

    x="Risk Segment",

    y="Default Rate",

    text="Default Rate",

    title="Observed Default Rate Across Descriptive Segments",

    color="Risk Segment",

    category_orders={
        "Risk Segment": risk_order
    },

    color_discrete_sequence=CHART_COLORS

)


fig.update_traces(

    texttemplate="%{y:.1f}%",

    textposition="outside"

)


fig.update_layout(

    template="plotly_white",

    yaxis_title="Observed Default Rate (%)",

    showlegend=False

)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# RULE DOCUMENTATION
# ============================================================

st.divider()

st.subheader("📋 EDA Segmentation Rules")


rules_df = pd.DataFrame({

    "Observed Condition": [

        "High Credit Burden",
        "High Annuity Burden",
        "Short Employment",
        "High Bureau Debt",
        "High Bureau Overdue",
        "Repeated Late Payments",
        "High Card Utilization"

    ],

    "Rule": [

        "Credit-to-Income ≥ 75th percentile",
        "Annuity-to-Income ≥ 75th percentile",
        "Employment < 3 years",
        "Bureau debt ≥ 75th percentile",
        "Bureau overdue > 75th percentile",
        "At least 3 late payments",
        "Average utilization ≥ 75%"

    ]

})


st.dataframe(
    rules_df,
    use_container_width=True,
    hide_index=True
)


st.markdown(
    """
    ### Segment Interpretation

    | Risk Score | Descriptive Segment |
    |---:|---|
    | 0–1 | Low Observed Risk |
    | 2–3 | Moderate Observed Risk |
    | 4–5 | Elevated Observed Risk |
    | 6–7 | High Observed Risk |

    ⚠️ These thresholds are used for **descriptive portfolio
    segmentation**. They are not trained, optimized or validated
    as a predictive model.
    """
)


# ============================================================
# RISK FLAG CONTRIBUTION
# ============================================================

st.subheader(
    "🔎 Contribution of Observed Risk Factors"
)


flag_counts = (

    filtered[risk_flags]
    .sum()
    .sort_values(ascending=False)
    .reset_index()

)


flag_counts.columns = [
    "Risk Factor",
    "Customers"
]


flag_names = {

    "HIGH_CREDIT_BURDEN":
        "High Credit Burden",

    "HIGH_ANNUITY_BURDEN":
        "High Annuity Burden",

    "SHORT_EMPLOYMENT":
        "Short Employment",

    "HIGH_BUREAU_DEBT":
        "High Bureau Debt",

    "HIGH_BUREAU_OVERDUE":
        "High Bureau Overdue",

    "REPEATED_LATE_PAYMENT":
        "Repeated Late Payments",

    "HIGH_CARD_UTILIZATION":
        "High Card Utilization"

}


flag_counts["Risk Factor"] = (

    flag_counts["Risk Factor"]
    .map(flag_names)

)


fig = px.bar(

    flag_counts,

    x="Customers",

    y="Risk Factor",

    orientation="h",

    text="Customers",

    title="Frequency of Observed Risk Conditions",

    color_discrete_sequence=[
        CHART_COLORS[0]
    ]

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
# DETAILED CUSTOMER TABLE
# ============================================================

st.divider()

st.subheader(
    "📄 Customer-Level Risk Segmentation"
)


display_columns = [

    "SK_ID_CURR",
    "TARGET",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "CREDIT_TO_INCOME",
    "ANNUITY_TO_INCOME",
    "EMPLOYMENT_YEARS",
    "TOTAL_BUREAU_DEBT",
    "TOTAL_BUREAU_OVERDUE",
    "LATE_PAYMENT_COUNT",
    "AVERAGE_PAYMENT_DELAY",
    "AVERAGE_CREDIT_CARD_UTILIZATION",
    "OBSERVED_RISK_SCORE",
    "RISK_SEGMENT"

]


display_columns = [

    col

    for col in display_columns

    if col in filtered.columns

]


with st.expander(
    "View Customer-Level Segmentation Table",
    expanded=False
):

    customer_table = (

        filtered[
            display_columns
        ]

        .sort_values(
            "OBSERVED_RISK_SCORE",
            ascending=False
        )

        .head(1000)

    )


    st.dataframe(

        customer_table,

        use_container_width=True,

        hide_index=True

    )


# ============================================================
# KEY OBSERVATIONS
# ============================================================

st.divider()

st.subheader("🔍 Key Observations")


segment_summary = (

    filtered
    .groupby(
        "RISK_SEGMENT",
        observed=False
    )
    .agg(

        Customers=(
            "SK_ID_CURR",
            "nunique"
        ),

        Average_Credit=(
            "AMT_CREDIT",
            "mean"
        ),

        Average_Income=(
            "AMT_INCOME_TOTAL",
            "mean"
        ),

        Default_Rate=(
            "TARGET",
            "mean"
        ),

        Average_Late_Payments=(
            "LATE_PAYMENT_COUNT",
            "mean"
        )

    )

    .reindex(risk_order)

)


largest_segment = (

    segment_summary["Customers"]
    .idxmax()

)


highest_default_segment = (

    segment_summary["Default_Rate"]
    .idxmax()

)


highest_late_payment_segment = (

    segment_summary["Average_Late_Payments"]
    .idxmax()

)


st.markdown(

    f"""
    - The largest observed segment in the current filter is
      **{largest_segment}**.

    - The segment with the highest observed default rate is
      **{highest_default_segment}**.

    - The segment with the highest average late-payment count is
      **{highest_late_payment_segment}**.

    - The segmentation combines multiple financial-behaviour
      indicators rather than relying on TARGET alone.

    - Customers with several simultaneous observed conditions
      receive a higher descriptive risk score.
    """

)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")


insights = [

    (
        "Risk segmentation provides a portfolio-monitoring view",
        "The rule-based segments make it easier to compare customers "
        "with different combinations of observed financial characteristics."
    ),

    (
        "Multiple indicators provide a broader view",
        "Credit burden, repayment behaviour, bureau exposure and "
        "utilization represent different dimensions of customer behaviour."
    ),

    (
        "Elevated segments should be investigated",
        "A descriptive risk segment identifies a group for further "
        "analysis. It does not mean every customer will default."
    ),

    (
        "Late-payment behaviour is important",
        "Customers with repeated historical payment delays can be "
        "separated from customers without those observed patterns."
    ),

    (
        "Bureau debt adds an external-credit perspective",
        "A customer may have a reasonable current application profile "
        "while also carrying substantial external debt."
    ),

    (
        "Credit utilization adds another financial-pressure indicator",
        "High utilization can indicate substantial use of available "
        "revolving credit."
    ),

    (
        "Affordability and repayment behaviour can overlap",
        "Customers may simultaneously exhibit high credit burden "
        "and repeated payment delays."
    ),

    (
        "Rates should be considered alongside customer counts",
        "A large segment can naturally contain more defaults simply "
        "because it contains more customers."
    ),

    (
        "Segmentation should be reviewed periodically",
        "The distribution of observed conditions can change as "
        "the portfolio changes."
    ),

    (
        "The approach is intentionally transparent",
        "Every customer can be traced back to the observed conditions "
        "that contributed to their descriptive segment."
    )

]


for i, (title, description) in enumerate(
    insights,
    start=1
):

    with st.expander(
        f"{i}. {title}",
        expanded=False
    ):

        st.write(description)


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.subheader("✅ Business Recommendations")


recommendations = [

    "Prioritize descriptive monitoring of Elevated and High Observed Risk segments.",

    "Review customers with multiple simultaneous affordability pressures.",

    "Create early-warning reports for repeated late installment payments.",

    "Monitor customers with high credit-to-income ratios.",

    "Track customers carrying substantial bureau debt.",

    "Monitor bureau overdue balances separately from total bureau debt.",

    "Track customers with consistently high credit-card utilization.",

    "Compare current credit exposure with external bureau obligations.",

    "Review customers combining high utilization and repeated payment delays.",

    "Use employment stability as an additional descriptive monitoring dimension.",

    "Do not automatically decline customers based solely on their descriptive segment.",

    "Investigate the underlying factors behind each segment before taking operational action.",

    "Refresh segmentation rules periodically as portfolio behaviour changes.",

    "Use Page 19 as a bridge between individual EDA pages and executive recommendations on Page 20.",

    "Use segment-level findings together with default-risk analysis to understand observed historical patterns."

]


for i, recommendation in enumerate(
    recommendations,
    start=1
):

    st.markdown(
        f"**{i}.** {recommendation}"
    )


# ============================================================
# DOWNLOAD
# ============================================================

st.divider()

st.subheader("⬇️ Download Segmentation Data")


download_columns = [

    col

    for col in display_columns

    if col in filtered.columns

]


segmentation_csv = (

    filtered[
        download_columns
    ]

    .to_csv(
        index=False
    )

)


st.download_button(

    label="Download Customer Risk Segmentation CSV",

    data=segmentation_csv,

    file_name="customer_risk_segmentation.csv",

    mime="text/csv"

)