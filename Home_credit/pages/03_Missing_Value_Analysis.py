import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data

st.set_page_config(page_title="Missing Value Analysis", page_icon="🔍", layout="wide")
load_css()
st.title("🔍 Missing Value Analysis")
st.caption("Deep dive into where and how much data is missing.")

df = load_data()
missing_pct = (df.isnull().mean() * 100).round(2)
missing_pct = missing_pct[missing_pct > 0].sort_values(ascending=False)

# ---- KPI row ----
total_missing = df.isnull().sum().sum()
overall_pct = df.isnull().mean().mean() * 100
c1, c2, c3, c4, c5 = st.columns(5)
with c1: kpi_card("Total missing values", f"{total_missing:,}")
with c2: kpi_card("Avg missing %", f"{overall_pct:.1f}%")
with c3: kpi_card("Columns with missing data", f"{len(missing_pct)}")
with c4: kpi_card("Columns above 30%", f"{(missing_pct > 30).sum()}")
with c5: kpi_card("Columns above 50%", f"{(missing_pct > 50).sum()}")

st.divider()

# ---- Slider-driven top-N chart ----
top_n = st.slider("Show top N columns by missing percentage", 5, min(50, len(missing_pct)), 20)
fig = px.bar(missing_pct.head(top_n), orientation="h",
             title=f"Top {top_n} columns by missing %",
             color_discrete_sequence=[CHART_COLORS[2]])
fig.update_layout(template="plotly_white", showlegend=False, yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    fig = px.histogram(missing_pct, nbins=20, title="Missing % distribution across columns",
                        color_discrete_sequence=[CHART_COLORS[1]])
    fig.update_layout(template="plotly_white", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    missing_by_dtype = df[missing_pct.index].isnull().sum().groupby(df[missing_pct.index].dtypes.astype(str)).sum()
    fig = px.bar(missing_by_dtype, title="Missing values by data type",
                 color_discrete_sequence=[CHART_COLORS[0]])
    fig.update_layout(template="plotly_white", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ---- Missingness heatmap (sampled for performance) ----
sample_size = st.slider("Rows to sample for the heatmap (larger = slower)", 200, 5000, 1000, step=200)
sample_cols = missing_pct.head(30).index
fig = px.imshow(df[sample_cols].sample(min(sample_size, len(df)), random_state=1).isnull().T,
                 aspect="auto", color_continuous_scale=["#F7F8FA", CHART_COLORS[2]],
                 title="Missingness heatmap (sampled rows, top 30 columns)")
fig.update_layout(template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# ---- Categorize columns into missing buckets ----
bins = [-0.1, 5, 20, 40, 60, 100]
labels = ["0–5%", "5–20%", "20–40%", "40–60%", "60%+"]
bucket_counts = pd.cut(missing_pct, bins=bins, labels=labels).value_counts().reindex(labels)
fig = px.bar(bucket_counts, title="Columns grouped by missing % range",
             color_discrete_sequence=[CHART_COLORS[3]])
fig.update_layout(template="plotly_white", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Preprocessing recommendations")
st.markdown("""
- **60%+ missing** → drop the column unless it's a known business-critical flag.
- **40–60% missing** → keep only if strongly predictive elsewhere; otherwise drop or flag.
- **20–40% missing** → impute (median/mode) and add a missing-indicator column to preserve the signal that it was missing.
- **5–20% missing** → straightforward median/mode imputation is usually safe.
- **0–5% missing** → drop the few affected rows, or impute — low risk either way.
""")