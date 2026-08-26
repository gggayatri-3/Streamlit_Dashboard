import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.theme import load_css, kpi_card, CHART_COLORS


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Bureau Balance Analysis",
    page_icon="📅",
    layout="wide"
)

load_css()

st.title("📅 Bureau Balance Analysis")
st.caption(
    "Monthly historical analysis of bureau account status, "
    "delinquency patterns, and credit-account behaviour."
)

st.divider()


# ============================================================
# BUSINESS OBJECTIVE
# ============================================================

with st.expander("🎯 Business Objective", expanded=True):
    st.markdown(
        """
        This page analyses the monthly history of bureau credit accounts
        using **bureau_balance.csv**.

        The analysis focuses on:

        - Monthly bureau records
        - Account status
        - Delinquency patterns
        - Closed periods
        - Active periods
        - Historical status trends
        - Customer-level bureau behaviour

        The objective is to understand how customers' external credit
        accounts behaved over time.

        **Important:** This is descriptive EDA. Historical account status
        patterns should not be interpreted as predictions.
        """
    )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_bureau_balance():

    possible_paths = [
        r"D:\Home_credit\data\raw\bureau_balance.csv",
        r"D:\Home_credit\raw_datasets\bureau_balance.csv",
        r"D:\Home_credit\bureau_balance.csv"
    ]

    for path in possible_paths:

        try:
            data = pd.read_csv(path)
            return data

        except FileNotFoundError:
            continue

    raise FileNotFoundError(
        "bureau_balance.csv was not found. "
        "Please check the location of bureau_balance.csv."
    )


bureau_balance = load_bureau_balance()


# ============================================================
# BASIC CLEANING
# ============================================================

bureau_balance = bureau_balance.copy()

bureau_balance["MONTHS_BALANCE"] = pd.to_numeric(
    bureau_balance["MONTHS_BALANCE"],
    errors="coerce"
)

bureau_balance["SK_ID_BUREAU"] = pd.to_numeric(
    bureau_balance["SK_ID_BUREAU"],
    errors="coerce"
)


# ============================================================
# STATUS DEFINITIONS
# ============================================================

# Home Credit bureau balance STATUS values:
#
# 0 = Current
# 1 = 1-30 days past due
# 2 = 31-60 days past due
# 3 = 61-90 days past due
# 4 = 91-120 days past due
# 5 = Over 120 days past due
# C = Closed
# X = Unknown / no loan for the month

status_mapping = {
    "0": "Current",
    "1": "1-30 DPD",
    "2": "31-60 DPD",
    "3": "61-90 DPD",
    "4": "91-120 DPD",
    "5": "120+ DPD",
    "C": "Closed",
    "X": "Unknown"
}

bureau_balance["STATUS_LABEL"] = (
    bureau_balance["STATUS"]
    .astype(str)
    .str.strip()
    .map(status_mapping)
    .fillna(
        bureau_balance["STATUS"]
        .astype(str)
    )
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Bureau Balance Filters")


status_options = ["All"] + sorted(
    bureau_balance["STATUS_LABEL"]
    .dropna()
    .unique()
    .tolist()
)

status_sel = st.sidebar.selectbox(
    "Account Status",
    status_options
)


# DPD filter
dpd_filter = st.sidebar.selectbox(
    "Delinquency Records",
    [
        "All Records",
        "Delinquency Only",
        "Non-Delinquency"
    ]
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = bureau_balance.copy()


if status_sel != "All":

    filtered = filtered[
        filtered["STATUS_LABEL"] == status_sel
    ]


if dpd_filter == "Delinquency Only":

    filtered = filtered[
        filtered["STATUS_LABEL"].isin(
            [
                "1-30 DPD",
                "31-60 DPD",
                "61-90 DPD",
                "91-120 DPD",
                "120+ DPD"
            ]
        )
    ]


elif dpd_filter == "Non-Delinquency":

    filtered = filtered[
        ~filtered["STATUS_LABEL"].isin(
            [
                "1-30 DPD",
                "31-60 DPD",
                "61-90 DPD",
                "91-120 DPD",
                "120+ DPD"
            ]
        )
    ]


# ============================================================
# EMPTY CHECK
# ============================================================

if filtered.empty:

    st.warning(
        "No records match the selected filters. "
        "Please adjust the filters."
    )

    st.stop()


# ============================================================
# DELINQUENCY FLAG
# ============================================================

delinquency_statuses = [
    "1-30 DPD",
    "31-60 DPD",
    "61-90 DPD",
    "91-120 DPD",
    "120+ DPD"
]

filtered["IS_DELINQUENT"] = (
    filtered["STATUS_LABEL"]
    .isin(delinquency_statuses)
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_records = len(filtered)

unique_bureau_accounts = (
    filtered["SK_ID_BUREAU"]
    .nunique()
)

most_common_status = (
    filtered["STATUS_LABEL"]
    .value_counts()
    .index[0]
)

delinquency_records = int(
    filtered["IS_DELINQUENT"].sum()
)

closed_records = int(
    (
        filtered["STATUS_LABEL"] == "Closed"
    ).sum()
)

active_records = int(
    (
        filtered["STATUS_LABEL"] == "Current"
    ).sum()
)

delinquency_percentage = (
    delinquency_records / total_records * 100
    if total_records > 0
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("📊 Bureau Balance Snapshot")

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card(
        "Monthly Bureau Records",
        f"{total_records:,}"
    )

with c2:
    kpi_card(
        "Unique Bureau Accounts",
        f"{unique_bureau_accounts:,}"
    )

with c3:
    kpi_card(
        "Most Common Status",
        most_common_status
    )

with c4:
    kpi_card(
        "Delinquency Records",
        f"{delinquency_records:,}"
    )


c5, c6, c7, c8 = st.columns(4)

with c5:
    kpi_card(
        "Closed Records",
        f"{closed_records:,}"
    )

with c6:
    kpi_card(
        "Current Records",
        f"{active_records:,}"
    )

with c7:
    kpi_card(
        "Delinquency %",
        f"{delinquency_percentage:.2f}%"
    )

with c8:

    months_range = (
        filtered["MONTHS_BALANCE"].max()
        - filtered["MONTHS_BALANCE"].min()
        if filtered["MONTHS_BALANCE"].notna().any()
        else 0
    )

    kpi_card(
        "History Span",
        f"{abs(months_range):,.0f} months"
    )


st.divider()


# ============================================================
# GRAPH 1 — STATUS DISTRIBUTION
# ============================================================

st.subheader("1️⃣ Bureau Account Status Distribution")

status_counts = (
    filtered["STATUS_LABEL"]
    .value_counts()
    .reset_index()
)

status_counts.columns = [
    "Status",
    "Records"
]

fig = px.bar(
    status_counts.sort_values("Records"),
    x="Records",
    y="Status",
    orientation="h",
    text="Records",
    title="Monthly Records by Bureau Account Status",
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


# ============================================================
# GRAPH 2 — STATUS PERCENTAGE
# ============================================================

st.subheader("2️⃣ Bureau Status Composition")

status_percentage = (
    filtered["STATUS_LABEL"]
    .value_counts(normalize=True)
    * 100
)

fig = px.pie(
    values=status_percentage.values,
    names=status_percentage.index,
    hole=0.55,
    title="Percentage of Bureau Monthly Records by Status",
    color_discrete_sequence=CHART_COLORS
)

fig.update_traces(
    texttemplate="%{percent:.1%}",
    hovertemplate=(
        "<b>%{label}</b><br>"
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
# GRAPH 3 — STATUS BY MONTH
# ============================================================

st.subheader("3️⃣ Account Status by Month")

monthly_status = (
    filtered.groupby(
        ["MONTHS_BALANCE", "STATUS_LABEL"]
    )
    .size()
    .reset_index(
        name="Records"
    )
)

monthly_status = monthly_status.sort_values(
    "MONTHS_BALANCE"
)

fig = px.bar(
    monthly_status,
    x="MONTHS_BALANCE",
    y="Records",
    color="STATUS_LABEL",
    title="Monthly Bureau Account Status Composition",
    labels={
        "MONTHS_BALANCE": "Months Before Current Application",
        "Records": "Records",
        "STATUS_LABEL": "Account Status"
    },
    barmode="stack"
)

fig.update_layout(
    template="plotly_white",
    legend_title="Status"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 4 — MONTHLY DELINQUENCY TREND
# ============================================================

st.subheader("4️⃣ Monthly Delinquency Trend")

monthly_dpd = (
    filtered.groupby("MONTHS_BALANCE")
    .agg(
        Total_Records=("IS_DELINQUENT", "size"),
        Delinquency_Records=(
            "IS_DELINQUENT",
            "sum"
        )
    )
    .reset_index()
)

monthly_dpd["Delinquency_Rate"] = (
    monthly_dpd["Delinquency_Records"]
    / monthly_dpd["Total_Records"]
    * 100
)

monthly_dpd = monthly_dpd.sort_values(
    "MONTHS_BALANCE"
)

fig = px.line(
    monthly_dpd,
    x="MONTHS_BALANCE",
    y="Delinquency_Rate",
    markers=True,
    title="Observed Monthly Bureau Delinquency Rate",
    labels={
        "MONTHS_BALANCE":
            "Months Before Current Application",
        "Delinquency_Rate":
            "Delinquency Rate (%)"
    }
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 5 — DPD SEVERITY
# ============================================================

st.subheader("5️⃣ Delinquency Severity Distribution")

dpd_statuses = [
    "1-30 DPD",
    "31-60 DPD",
    "61-90 DPD",
    "91-120 DPD",
    "120+ DPD"
]

dpd_counts = (
    filtered[
        filtered["STATUS_LABEL"].isin(
            dpd_statuses
        )
    ]["STATUS_LABEL"]
    .value_counts()
    .reindex(
        dpd_statuses,
        fill_value=0
    )
    .reset_index()
)

dpd_counts.columns = [
    "DPD Level",
    "Records"
]

fig = px.bar(
    dpd_counts,
    x="DPD Level",
    y="Records",
    text="Records",
    title="Bureau Delinquency Severity",
    color_discrete_sequence=[CHART_COLORS[1]]
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
# GRAPH 6 — STATUS HEATMAP
# ============================================================

st.subheader("6️⃣ Bureau Status Heatmap")

heatmap_data = (
    filtered.groupby(
        [
            "MONTHS_BALANCE",
            "STATUS_LABEL"
        ]
    )
    .size()
    .reset_index(
        name="Records"
    )
)

heatmap_pivot = (
    heatmap_data
    .pivot(
        index="STATUS_LABEL",
        columns="MONTHS_BALANCE",
        values="Records"
    )
    .fillna(0)
)

fig = px.imshow(
    heatmap_pivot,
    aspect="auto",
    title="Bureau Account Status Across Historical Months",
    labels={
        "x": "Months Before Current Application",
        "y": "Account Status",
        "color": "Records"
    }
)

fig.update_layout(
    template="plotly_white",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# GRAPH 7 — DELINQUENCY VS CURRENT
# ============================================================

st.subheader("7️⃣ Current vs Delinquent Records")

comparison = pd.DataFrame({
    "Category": [
        "Current",
        "Delinquent"
    ],
    "Records": [
        (
            filtered["STATUS_LABEL"]
            == "Current"
        ).sum(),
        filtered["IS_DELINQUENT"].sum()
    ]
})

fig = px.bar(
    comparison,
    x="Category",
    y="Records",
    text="Records",
    title="Current vs Delinquent Bureau Records",
    color_discrete_sequence=[CHART_COLORS[2]]
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
# CUSTOMER-LEVEL FEATURES
# ============================================================

st.divider()

st.subheader("👥 Customer-Level Bureau Balance Features")

# IMPORTANT:
# bureau_balance.csv contains SK_ID_BUREAU rather than SK_ID_CURR.
#
# Therefore customer-level features require joining bureau_balance
# with bureau.csv.

@st.cache_data
def load_bureau_mapping():

    possible_paths = [
        r"D:\Home_credit\data\raw\bureau.csv",
        r"D:\Home_credit\raw_datasets\bureau.csv",
        r"D:\Home_credit\bureau.csv"
    ]

    for path in possible_paths:

        try:
            bureau_map = pd.read_csv(
                path,
                usecols=[
                    "SK_ID_CURR",
                    "SK_ID_BUREAU"
                ]
            )

            return bureau_map

        except FileNotFoundError:
            continue

    return None


bureau_mapping = load_bureau_mapping()


if bureau_mapping is not None:

    customer_balance = filtered.merge(
        bureau_mapping,
        on="SK_ID_BUREAU",
        how="left"
    )

    customer_features = (
        customer_balance
        .groupby("SK_ID_CURR")
        .agg(
            MONTHLY_BUREAU_RECORDS=(
                "SK_ID_BUREAU",
                "count"
            ),
            UNIQUE_BUREAU_ACCOUNTS=(
                "SK_ID_BUREAU",
                "nunique"
            ),
            MONTHS_WITH_DELINQUENCY=(
                "IS_DELINQUENT",
                "sum"
            ),
            CLOSED_MONTHS=(
                "STATUS_LABEL",
                lambda x: (
                    x == "Closed"
                ).sum()
            ),
            ACTIVE_MONTHS=(
                "STATUS_LABEL",
                lambda x: (
                    x == "Current"
                ).sum()
            )
        )
        .reset_index()
    )

    # Highest numerical DPD severity
    severity_mapping = {
        "Current": 0,
        "1-30 DPD": 1,
        "31-60 DPD": 2,
        "61-90 DPD": 3,
        "91-120 DPD": 4,
        "120+ DPD": 5,
        "Closed": 0,
        "Unknown": 0
    }

    customer_balance["DPD_SEVERITY"] = (
        customer_balance["STATUS_LABEL"]
        .map(severity_mapping)
        .fillna(0)
    )

    max_dpd = (
        customer_balance
        .groupby("SK_ID_CURR")["DPD_SEVERITY"]
        .max()
        .reset_index(
            name="MAX_DELINQUENCY_LEVEL"
        )
    )

    customer_features = customer_features.merge(
        max_dpd,
        on="SK_ID_CURR",
        how="left"
    )


    # ========================================================
    # CUSTOMER KPIs
    # ========================================================

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        kpi_card(
            "Customers Analysed",
            f"{len(customer_features):,}"
        )

    with f2:
        kpi_card(
            "Avg Delinquent Months",
            f"{customer_features['MONTHS_WITH_DELINQUENCY'].mean():.1f}"
        )

    with f3:
        customers_with_dpd = (
            customer_features[
                "MONTHS_WITH_DELINQUENCY"
            ] > 0
        ).sum()

        kpi_card(
            "Customers with Delinquency",
            f"{customers_with_dpd:,}"
        )

    with f4:
        severe_dpd = (
            customer_features[
                "MAX_DELINQUENCY_LEVEL"
            ] >= 3
        ).sum()

        kpi_card(
            "Customers with 61+ DPD",
            f"{severe_dpd:,}"
        )


    # ========================================================
    # CUSTOMER DELINQUENCY DISTRIBUTION
    # ========================================================

    st.subheader(
        "📊 Customer Months with Delinquency"
    )

    delinquency_distribution = (
        customer_features[
            "MONTHS_WITH_DELINQUENCY"
        ]
        .value_counts()
        .sort_index()
        .head(20)
        .reset_index()
    )

    delinquency_distribution.columns = [
        "Delinquent Months",
        "Customers"
    ]

    fig = px.bar(
        delinquency_distribution,
        x="Delinquent Months",
        y="Customers",
        text="Customers",
        title="Number of Customers by Delinquent Months",
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


    # ========================================================
    # CUSTOMER TABLE
    # ========================================================

    st.subheader(
        "📋 Customer-Level Bureau Balance Features"
    )

    st.dataframe(
        customer_features.head(1000),
        use_container_width=True
    )

else:

    st.warning(
        "bureau.csv could not be found. "
        "Customer-level features require the "
        "SK_ID_BUREAU → SK_ID_CURR relationship."
    )


# ============================================================
# KEY OBSERVATIONS
# ============================================================

st.divider()

st.subheader("🔍 Key Observations")

highest_dpd_status = (
    dpd_counts.loc[
        dpd_counts["Records"].idxmax(),
        "DPD Level"
    ]
    if dpd_counts["Records"].sum() > 0
    else "No delinquency records"
)

highest_dpd_count = (
    dpd_counts["Records"].max()
    if len(dpd_counts) > 0
    else 0
)

st.markdown(
    f"""
- The filtered bureau balance dataset contains
  **{total_records:,} monthly records** across
  **{unique_bureau_accounts:,} unique bureau accounts**.
- The most frequently observed account status is
  **{most_common_status}**.
- There are **{delinquency_records:,} delinquency records**, representing
  approximately **{delinquency_percentage:.2f}%** of the filtered records.
- Among delinquency categories, **{highest_dpd_status}** is the most
  frequently observed level with **{highest_dpd_count:,} records**.
- There are **{closed_records:,} records classified as closed**.
"""
)


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.subheader("💡 Business Insights")

st.markdown(
    """
### 1. Monthly history provides more detail than a single account status

A bureau account can move through different statuses over time.
Analysing monthly records helps reveal the historical behaviour of
external accounts.

### 2. Delinquency severity matters

Not all delinquency records represent the same level of repayment stress.
The dashboard separates 1–30 DPD, 31–60 DPD, 61–90 DPD, 91–120 DPD and
120+ DPD.

### 3. Repeated delinquency is more informative than a single event

A customer appearing in delinquency records across multiple months has a
different historical pattern from a customer with only one delinquent month.

### 4. Current and closed accounts should be distinguished

Current records indicate ongoing account activity, while closed records
represent historical account periods.

### 5. Customer-level aggregation prevents account-level distortion

A customer with several bureau accounts may generate many monthly records.
Customer-level features therefore provide an additional perspective.

### 6. Historical bureau behaviour can complement current application analysis

Bureau balance information should be interpreted together with current
credit burden, previous applications and installment repayment behaviour.
"""
)


# ============================================================
# BUSINESS RECOMMENDATIONS
# ============================================================

st.subheader("✅ Business Recommendations")

st.markdown(
    """
1. **Monitor customers with repeated bureau delinquency months** rather
   than focusing only on isolated delinquency events.

2. **Separate mild and severe delinquency** in portfolio monitoring.

3. **Track customers with 61+ DPD history** as a distinct analytical group.

4. **Combine bureau delinquency with total bureau debt** from Page 13.

5. **Compare bureau delinquency history with current
   credit-to-income ratios** from Page 10.

6. **Combine historical bureau status with installment payment behaviour**
   from Page 17.

7. **Monitor trends in delinquency across historical months** to identify
   changing portfolio patterns.

8. **Use customer-level delinquency features** such as
   `MONTHS_WITH_DELINQUENCY` and `MAX_DELINQUENCY_LEVEL` for descriptive
   portfolio analysis.

9. **Investigate customers with repeated severe delinquency** through
   detailed account-level records.

10. **Do not treat every bureau status as a risk signal**; distinguish
    current, closed, unknown and different delinquency levels.

11. **Use minimum customer-volume checks** when comparing groups with
    different historical bureau exposure.

12. **Integrate bureau balance findings with the final executive dashboard**
    to support evidence-based business recommendations.
"""
)


# ============================================================
# DOWNLOAD
# ============================================================

st.divider()

st.subheader("⬇️ Download Bureau Balance Data")

filtered_csv = filtered.to_csv(
    index=False
)

st.download_button(
    label="Download Filtered Bureau Balance Data",
    data=filtered_csv,
    file_name="filtered_bureau_balance.csv",
    mime="text/csv"
)


# ============================================================
# RAW DATA TABLE
# ============================================================

with st.expander("📄 View Filtered Bureau Balance Records"):

    st.dataframe(
        filtered.head(1000),
        use_container_width=True
    )