import streamlit as st
from utils.theme import load_css

st.set_page_config(
    page_title="Home Credit Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)
load_css()

st.title("Home Credit Risk & Portfolio Analytics")
st.caption("A 20-page exploratory data analysis suite — preprocessing, feature engineering, and business insights across the full Home Credit dataset.")

st.divider()

cols = st.columns(4)
sections = [
    ("Data Quality", "Missing values, duplicates, dtype checks"),
    ("Customer & Demographics", "Who the borrowers are"),
    ("Credit & Affordability", "Loan burden vs income"),
    ("Risk & Repayment", "Default patterns, bureau history, payment behavior"),
]
for col, (title, desc) in zip(cols, sections):
    with col:
        st.markdown(f"""
            <div class="kpi-card" style="min-height:120px">
                <div class="kpi-value" style="font-size:17px">{title}</div>
                <div class="kpi-label" style="margin-top:8px">{desc}</div>
            </div>
        """, unsafe_allow_html=True)

st.divider()
st.markdown("Use the sidebar to navigate through the 20 analysis pages.")