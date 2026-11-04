"""
PulseIQ Governed Metric Catalog (Task 4 View)
=============================================
Interactive dictionary of all 28 officially governed metrics with privacy rules.
"""

import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(page_title="PulseIQ | Metric Catalog", page_icon="📖", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .cat-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        border-left: 6px solid #3B82F6;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="cat-header">
    <div style="font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #94A3B8; margin-bottom: 4px;">
        PulseIQ Semantic Layer
    </div>
    <h1 style="margin: 0; font-size: 28px; font-weight: 800; color: white;">Governed Metric Catalog (28 Metrics)</h1>
    <p style="margin: 6px 0 0 0; color: #CBD5E1; font-size: 14px;">
        Single source of truth definitions, formulas, grains, and privacy suppression thresholds.
    </p>
</div>
""", unsafe_allow_html=True)

con = duckdb.connect("pulseiq.duckdb", read_only=True)
df_cat = con.execute("SELECT * FROM metrics.metric_catalog ORDER BY metric_id").fetchdf()
con.close()

# Filters
col_search, col_owner = st.columns([2, 1])
with col_search:
    search = st.text_input("🔍 Search Metric Name or Keyword:", "")
with col_owner:
    owners = ["All"] + sorted(df_cat['owner_team'].dropna().unique().tolist())
    selected_owner = st.selectbox("Filter by Owner Team:", owners)

filtered_cat = df_cat.copy()
if search:
    filtered_cat = filtered_cat[
        filtered_cat['metric_name'].str.contains(search, case=False, na=False) |
        filtered_cat['business_definition'].str.contains(search, case=False, na=False)
    ]
if selected_owner != "All":
    filtered_cat = filtered_cat[filtered_cat['owner_team'] == selected_owner]

st.markdown(f"**Showing {len(filtered_cat)} of {len(df_cat)} governed metrics:**")

st.dataframe(
    filtered_cat[['metric_id', 'metric_name', 'business_definition', 'formula', 'grain', 'owner_team', 'unit', 'min_group_size']],
    width='stretch',
    hide_index=True
)

st.markdown("---")
st.markdown("### 🔒 Small-Group Privacy Rule Architecture")
st.info("""
**Executive Protection & GDPR Compliance:**  
Any query sliced below the `min_group_size` threshold (e.g., Department `D00` with 1 CEO, or teams with < 5 members) automatically suppresses sensitive values with `NULL` and flags `is_privacy_masked = TRUE`. This guarantees that individual salaries, leave reasons, and turnover risks can never be inferred from public dashboards.
""")
