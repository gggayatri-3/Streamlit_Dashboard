import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data

st.set_page_config(page_title="Risk Factor Exploration", page_icon="🔎", layout="wide")
load_css()

st.title("🔎 Risk Factor Exploration")
st.caption("Explore observed relationships between customer characteristics, affordability measures, and historical default outcomes.")
st.divider()

with st.expander("🎯 Business Objective", expanded=True):
    st.markdown("""
    This page explores observed relationships between **TARGET** and age,
    income, credit, annuity, employment, education, occupation, family size,
    and affordability ratios.

    **Important:** These are historical EDA relationships, not predictions or causal findings.
    """)

df = load_data()

# ---------------- FILTERS ----------------
st.sidebar.header("🔎 Portfolio Filters")

filters = {
    "Gender": "CODE_GENDER",
    "Age Group": "AGE_GROUP",
    "Income Group": "INCOME_GROUP",
    "Education": "NAME_EDUCATION_TYPE",
    "Employment Group": "EMPLOYMENT_GROUP"
}

selected = {}
for label, col in filters.items():
    opts = ["All"] + sorted(df[col].dropna().unique().tolist())
    selected[col] = st.sidebar.selectbox(label, opts)

default_sel = st.sidebar.selectbox(
    "Default Status", ["All", "Non-Default", "Default"]
)

filtered = df.copy()

for col, value in selected.items():
    if value != "All":
        filtered = filtered[filtered[col] == value]

if default_sel == "Default":
    filtered = filtered[filtered["TARGET"] == 1]
elif default_sel == "Non-Default":
    filtered = filtered[filtered["TARGET"] == 0]

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ---------------- HELPERS ----------------
def band_risk(data, column, bins, labels):
    temp = data[[column, "TARGET"]].copy()
    temp["Band"] = pd.cut(temp[column], bins=bins, labels=labels, include_lowest=True)

    out = (
        temp.dropna(subset=["Band"])
        .groupby("Band", observed=False)["TARGET"]
        .agg(Customers="size", Defaults="sum", Default_Rate="mean")
        .reset_index()
    )
    out["Default_Rate"] *= 100
    return out


def risk_bar(data, x, title, color, y="Default_Rate", horizontal=False):
    fig = px.bar(
        data,
        x=x if not horizontal else y,
        y=y if not horizontal else x,
        orientation="h" if horizontal else "v",
        text=y,
        title=title,
        color_discrete_sequence=[color]
    )
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_layout(template="plotly_white", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ---------------- KPIs ----------------
total = len(filtered)
defaults = int(filtered["TARGET"].sum())
default_rate = filtered["TARGET"].mean() * 100

cti = filtered["CREDIT_TO_INCOME"].replace([np.inf, -np.inf], np.nan)
ati = filtered["ANNUITY_TO_INCOME"].replace([np.inf, -np.inf], np.nan)

kpis = [
    ("Customers", f"{total:,}"),
    ("Default Customers", f"{defaults:,}"),
    ("Observed Default Rate", f"{default_rate:.2f}%"),
    ("Avg Credit / Income", f"{cti.mean():.2f}x"),
    ("Median Credit / Income", f"{cti.median():.2f}x"),
    ("Avg Annuity / Income", f"{ati.mean():.2%}")
]

st.subheader("📊 Risk Factor Snapshot")
cols = st.columns(6)

for col, (label, value) in zip(cols, kpis):
    with col:
        kpi_card(label, value)

st.divider()

# ---------------- AGE ----------------
st.subheader("1️⃣ Age Group vs Observed Default Rate")

age_risk = (
    filtered.groupby("AGE_GROUP")["TARGET"]
    .agg(Customers="size", Defaults="sum", Default_Rate="mean")
    .reset_index()
)
age_risk["Default_Rate"] *= 100

risk_bar(
    age_risk,
    "AGE_GROUP",
    "Observed Default Rate by Age Group",
    CHART_COLORS[0]
)

# ---------------- CREDIT BAND ----------------
st.subheader("2️⃣ Credit Band vs Observed Default Rate")

credit_risk = band_risk(
    filtered,
    "AMT_CREDIT",
    [0, 100000, 250000, 500000, 750000, 1000000, 1500000, 2500000, np.inf],
    ["< ₹100K", "₹100K–250K", "₹250K–500K", "₹500K–750K",
     "₹750K–1M", "₹1M–1.5M", "₹1.5M–2.5M", "₹2.5M+"]
)

risk_bar(
    credit_risk,
    "Band",
    "Observed Default Rate by Credit Band",
    CHART_COLORS[1]
)

# ---------------- INCOME BAND ----------------
st.subheader("3️⃣ Income Band vs Observed Default Rate")

income_risk = band_risk(
    filtered,
    "AMT_INCOME_TOTAL",
    [0, 50000, 100000, 150000, 250000, 500000, 1000000, np.inf],
    ["< ₹50K", "₹50K–100K", "₹100K–150K", "₹150K–250K",
     "₹250K–500K", "₹500K–1M", "₹1M+"]
)

risk_bar(
    income_risk,
    "Band",
    "Observed Default Rate by Income Band",
    CHART_COLORS[2]
)

# ---------------- EMPLOYMENT ----------------
st.subheader("4️⃣ Employment Group vs Observed Default Rate")

employment_risk = (
    filtered.groupby("EMPLOYMENT_GROUP")["TARGET"]
    .agg(Customers="size", Defaults="sum", Default_Rate="mean")
    .reset_index()
)
employment_risk["Default_Rate"] *= 100
employment_risk = employment_risk.sort_values("Default_Rate")

risk_bar(
    employment_risk,
    "EMPLOYMENT_GROUP",
    "Observed Default Rate by Employment Group",
    CHART_COLORS[3],
    horizontal=True
)

# ---------------- CREDIT TO INCOME ----------------
st.subheader("5️⃣ Credit-to-Income Band vs Default")

cti_risk = band_risk(
    filtered,
    "CREDIT_TO_INCOME",
    [0, 1, 2, 3, 4, 5, 7.5, 10, np.inf],
    ["<1×", "1–2×", "2–3×", "3–4×", "4–5×",
     "5–7.5×", "7.5–10×", "10×+"]
)

risk_bar(
    cti_risk,
    "Band",
    "Observed Default Rate by Credit-to-Income Band",
    CHART_COLORS[0]
)

# ---------------- ANNUITY TO INCOME ----------------
st.subheader("6️⃣ Annuity-to-Income Band vs Default")

ati_risk = band_risk(
    filtered,
    "ANNUITY_TO_INCOME",
    [0, .10, .20, .30, .40, .50, .75, 1, np.inf],
    ["<10%", "10–20%", "20–30%", "30–40%",
     "40–50%", "50–75%", "75–100%", "100%+"]
)

risk_bar(
    ati_risk,
    "Band",
    "Observed Default Rate by Annuity-to-Income Band",
    CHART_COLORS[1]
)

# ---------------- CORRELATION ----------------
st.divider()
st.subheader("7️⃣ Correlation Heatmap")

corr_cols = [
    "AGE_YEARS", "EMPLOYMENT_YEARS", "AMT_INCOME_TOTAL",
    "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE",
    "CNT_CHILDREN", "CNT_FAM_MEMBERS", "CREDIT_TO_INCOME",
    "ANNUITY_TO_INCOME", "GOODS_TO_INCOME", "CREDIT_TO_GOODS",
    "INCOME_PER_FAMILY_MEMBER", "TARGET"
]

corr_cols = [c for c in corr_cols if c in filtered.columns]
corr = filtered[corr_cols].select_dtypes(include=np.number).corr()

fig = px.imshow(
    corr,
    text_auto=".2f",
    aspect="auto",
    title="Correlation Between Numerical Risk Factors"
)
fig.update_layout(template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# ---------------- TARGET CORRELATION ----------------
st.subheader("📌 Variables Most Associated with TARGET")

target_corr = (
    corr["TARGET"]
    .drop("TARGET")
    .sort_values(key=abs, ascending=False)
    .head(12)
    .sort_values()
    .reset_index()
)
target_corr.columns = ["Variable", "Correlation"]

fig = px.bar(
    target_corr,
    x="Correlation",
    y="Variable",
    orientation="h",
    text="Correlation",
    title="Strongest Observed Linear Associations with TARGET",
    color_discrete_sequence=[CHART_COLORS[2]]
)
fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
fig.update_layout(template="plotly_white", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# ---------------- MULTIVARIATE ----------------
st.divider()
st.subheader("8️⃣ Multivariate Risk Exploration")
st.caption("Explore income, credit burden, age and observed default together.")

scatter_cols = [
    "AMT_INCOME_TOTAL", "AMT_CREDIT", "TARGET",
    "AGE_GROUP", "INCOME_GROUP"
]

scatter = filtered[scatter_cols].dropna()

if len(scatter) > 15000:
    scatter = scatter.sample(15000, random_state=42)

scatter["Default Status"] = scatter["TARGET"].map({
    0: "Non-Default",
    1: "Default"
})

fig = px.scatter(
    scatter,
    x="AMT_INCOME_TOTAL",
    y="AMT_CREDIT",
    color="Default Status",
    facet_col="AGE_GROUP",
    hover_data=["INCOME_GROUP"],
    opacity=.55,
    title="Income vs Credit Amount by Age Group and Default Status"
)
fig.update_layout(template="plotly_white", height=550)
st.plotly_chart(fig, use_container_width=True)

# ---------------- SUMMARY TABLE ----------------
st.divider()
st.subheader("📋 Risk Factor Summary Table")

dimension = st.selectbox(
    "Select factor",
    ["AGE_GROUP", "INCOME_GROUP", "EMPLOYMENT_GROUP"]
)

summary = (
    filtered.groupby(dimension)["TARGET"]
    .agg(Customers="size", Defaults="sum", Default_Rate="mean")
    .reset_index()
)
summary["Default_Rate"] *= 100
summary = summary.sort_values("Default_Rate", ascending=False)

st.dataframe(
    summary.style.format({
        "Customers": "{:,.0f}",
        "Defaults": "{:,.0f}",
        "Default_Rate": "{:.2f}%"
    }),
    use_container_width=True
)

# ---------------- OBSERVATIONS ----------------
st.subheader("🔍 Key Observations")

def highest(data, column):
    if data.empty:
        return "N/A", 0
    row = data.loc[data["Default_Rate"].idxmax()]
    return str(row[column]), row["Default_Rate"]

age_name, age_rate = highest(age_risk, "AGE_GROUP")
income_name, income_rate = highest(income_risk, "Band")
emp_name, emp_rate = highest(employment_risk, "EMPLOYMENT_GROUP")
cti_name, cti_rate = highest(cti_risk, "Band")
ati_name, ati_rate = highest(ati_risk, "Band")

st.markdown(f"""
- Filtered portfolio: **{total:,} customers**, with an observed default rate of **{default_rate:.2f}%**.
- Highest age-group default rate: **{age_name} ({age_rate:.2f}%)**.
- Highest income-band default rate: **{income_name} ({income_rate:.2f}%)**.
- Highest employment-group default rate: **{emp_name} ({emp_rate:.2f}%)**.
- Highest displayed Credit-to-Income band: **{cti_name} ({cti_rate:.2f}%)**.
- Highest displayed Annuity-to-Income band: **{ati_name} ({ati_rate:.2f}%)**.
""")

# ---------------- INSIGHTS ----------------
st.subheader("💡 Business Insights")

st.markdown("""
- Affordability ratios provide context beyond absolute loan amounts.
- Income, age and employment groups can show different historical default patterns.
- Credit and income should be analysed together rather than independently.
- Multivariate analysis can reveal combinations of characteristics associated with different outcomes.
- Correlation indicates association, **not causation**.
- Small groups can produce unstable default rates, so customer volume should always be considered.
""")

# ---------------- RECOMMENDATIONS ----------------
st.subheader("✅ Business Recommendations")

st.markdown("""
1. Monitor Credit-to-Income and Annuity-to-Income ratios.
2. Compare credit exposure relative to customer income.
3. Review high-default bands together with their customer volumes.
4. Use employment and age as supporting portfolio-monitoring dimensions.
5. Combine affordability findings with repayment behaviour from **Page 17**.
6. Use correlation as an EDA screening tool, not as causal evidence.
7. Avoid acting on very small groups without additional validation.
8. Use multiple customer and financial dimensions for portfolio monitoring.
""")

# ---------------- DOWNLOAD ----------------
st.divider()

with st.expander("📄 View Filtered Risk Factor Records"):
    display_cols = [
        "SK_ID_CURR", "TARGET", "CODE_GENDER", "AGE_YEARS", "AGE_GROUP",
        "EMPLOYMENT_YEARS", "EMPLOYMENT_GROUP", "AMT_INCOME_TOTAL",
        "AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE",
        "CREDIT_TO_INCOME", "ANNUITY_TO_INCOME", "GOODS_TO_INCOME",
        "CREDIT_TO_GOODS", "INCOME_PER_FAMILY_MEMBER",
        "NAME_EDUCATION_TYPE", "OCCUPATION_TYPE"
    ]

    display_cols = [c for c in display_cols if c in filtered.columns]

    st.dataframe(
        filtered[display_cols].head(1000),
        use_container_width=True
    )

    st.download_button(
        "⬇️ Download Filtered Risk Factor Data",
        filtered[display_cols].to_csv(index=False),
        "risk_factor_filtered_data.csv",
        "text/csv"
    )