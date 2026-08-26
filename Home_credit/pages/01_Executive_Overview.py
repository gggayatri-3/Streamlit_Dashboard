import streamlit as st
import pandas as pd
import plotly.express as px
from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data          # your existing loader

st.set_page_config(page_title="Executive Overview", page_icon="📊", layout="wide")
load_css()
st.title("📊 Executive Portfolio Overview")
st.caption("High-level snapshot of the Home Credit loan portfolio.")

df = load_data()  # cached in your data_loader.py

# ---- Sidebar filters ----
st.sidebar.header("Filters")
gender_options = ["All"] + sorted(df["CODE_GENDER"].dropna().unique().tolist())
gender_sel = st.sidebar.selectbox("Gender", gender_options)

income_options = ["All"] + sorted(df["NAME_INCOME_TYPE"].dropna().unique().tolist())
income_sel = st.sidebar.selectbox("Income type", income_options)

filtered = df.copy()
if gender_sel != "All":
    filtered = filtered[filtered["CODE_GENDER"] == gender_sel]
if income_sel != "All":
    filtered = filtered[filtered["NAME_INCOME_TYPE"] == income_sel]

# ---- KPI row ----
c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Total customers", f"{len(filtered):,}")
with c2: kpi_card("Default rate", f"{filtered['TARGET'].mean()*100:.1f}%")
with c3: kpi_card("Avg credit amount", f"₹{filtered['AMT_CREDIT'].mean():,.0f}")
with c4: kpi_card("Avg income", f"₹{filtered['AMT_INCOME_TOTAL'].mean():,.0f}")

st.divider()

# ---- Charts ----
col1, col2 = st.columns([1.4, 1])

with col1:
    fig = px.histogram(filtered, x="AMT_CREDIT", nbins=40,
                        title="Credit amount distribution",
                        color_discrete_sequence=[CHART_COLORS[0]])
    fig.update_layout(template="plotly_white", margin=dict(t=40, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    default_counts = filtered["TARGET"].value_counts().rename({0: "No default", 1: "Default"})
    fig = px.pie(values=default_counts.values, names=default_counts.index, hole=0.55,
                 title="Default split", color_discrete_sequence=[CHART_COLORS[0], CHART_COLORS[2]])
    fig.update_layout(template="plotly_white", margin=dict(t=40, l=10, r=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

risk_by_income = filtered.groupby("NAME_INCOME_TYPE")["TARGET"].mean().sort_values() * 100
fig = px.bar(risk_by_income, orientation="h", title="Default rate by income type (%)",
             color_discrete_sequence=[CHART_COLORS[1]])
fig.update_layout(template="plotly_white", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.divider()
with st.expander("View underlying data"):
    st.dataframe(filtered.head(500))
    st.download_button("Download filtered data as CSV", filtered.to_csv(index=False), "filtered_data.csv")

st.subheader("Key observations")
st.markdown(f"""
- Overall default rate in the current filter is **{filtered['TARGET'].mean()*100:.1f}%**.
- The largest income segment is **{filtered['NAME_INCOME_TYPE'].mode()[0]}**.
""")

st.subheader("Business recommendations")
st.markdown("""
1. Prioritize manual review for income segments with above-average default rates.
2. Track credit exposure concentration by income type quarterly.
3. Use this filtered view as a starting point before drilling into affordability ratios (Page 10).
""")