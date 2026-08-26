import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.theme import load_css, kpi_card, CHART_COLORS
from utils.data_loader import load_data

st.set_page_config(page_title="Data Quality", page_icon="🧹", layout="wide")
load_css()
st.title("🧹 Data Quality Dashboard")
st.caption("Column-level health check before any cleaning or feature work.")

df = load_data()

# ---- KPI row ----
n_rows, n_cols = df.shape
numeric_cols = df.select_dtypes(include="number").columns
categorical_cols = df.select_dtypes(exclude="number").columns
missing_cells = df.isnull().sum().sum()
duplicate_rows = df.duplicated().sum()
memory_mb = df.memory_usage(deep=True).sum() / 1e6
unique_customers = df["SK_ID_CURR"].nunique() if "SK_ID_CURR" in df.columns else n_rows

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Rows", f"{n_rows:,}")
with c2: kpi_card("Columns", f"{n_cols}")
with c3: kpi_card("Numerical columns", f"{len(numeric_cols)}")
with c4: kpi_card("Categorical columns", f"{len(categorical_cols)}")

c5, c6, c7, c8 = st.columns(4)
with c5: kpi_card("Missing cells", f"{missing_cells:,}")
with c6: kpi_card("Duplicate rows", f"{duplicate_rows:,}")
with c7: kpi_card("Memory usage", f"{memory_mb:.1f} MB")
with c8: kpi_card("Unique customers", f"{unique_customers:,}")

st.divider()

# ---- Column summary table ----
summary = pd.DataFrame({
    "dtype": df.dtypes.astype(str),
    "missing_count": df.isnull().sum(),
    "missing_pct": (df.isnull().mean() * 100).round(2),
    "unique_values": df.nunique(),
})
for stat in ["min", "max", "mean", "median"]:
    summary[stat] = df[numeric_cols].agg(stat).reindex(summary.index)

# slider: only show columns with missing % above a chosen threshold
min_missing = st.slider("Show columns with missing % at or above", 0, 100, 0, step=5)
st.dataframe(summary[summary["missing_pct"] >= min_missing].sort_values("missing_pct", ascending=False))

st.divider()

# ---- Charts ----
col1, col2 = st.columns(2)

with col1:
    dtype_counts = df.dtypes.astype(str).value_counts()
    fig = px.bar(dtype_counts, title="Column data types",
                 color_discrete_sequence=[CHART_COLORS[0]])
    fig.update_layout(template="plotly_white", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    completeness = 100 - (missing_cells / (n_rows * n_cols) * 100)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=completeness,
        title={"text": "Dataset completeness (%)"},
        gauge={"axis": {"range": [0, 100]}, "bar": {"color": CHART_COLORS[0]}},
    ))
    st.plotly_chart(fig, use_container_width=True)

top_n = st.slider("Number of columns to show in the unique-values chart", 5, 40, 15)
unique_by_col = df.nunique().sort_values(ascending=False).head(top_n)
fig = px.bar(unique_by_col, orientation="h", title=f"Top {top_n} columns by unique values",
             color_discrete_sequence=[CHART_COLORS[1]])
fig.update_layout(template="plotly_white", showlegend=False)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Key observations")
worst = summary.sort_values("missing_pct", ascending=False).head(3)
st.markdown(f"""
- {len(summary[summary['missing_pct'] > 0])} columns contain at least some missing data.
- The columns with the most missingness are: **{', '.join(worst.index)}**.
- {duplicate_rows} duplicate rows detected across {n_rows:,} total rows.
""")

st.subheader("Preprocessing strategy")
st.markdown("""
1. Columns above 50% missing → candidates for dropping unless business-critical.
2. Columns between 5–50% missing → impute with median (numeric) or mode (categorical), or add a missing-indicator flag.
3. Verify `SK_ID_CURR` uniqueness before merging with bureau/previous-application tables.
""")