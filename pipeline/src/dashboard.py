import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Config
st.set_page_config(page_title="Retail Ops Intelligence", layout="wide")

st.title("Retail Operational Intelligence & Personalization Suite")
st.markdown("### Unified Product & Inventory Data Harmonization Pipeline")

# Load Data
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # pipeline/src
# Go up one level to find data
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")

PROCESSED_PATH = os.path.join(DATA_DIR, "processed", "inventory_fact.csv")
QUARANTINE_PATH = os.path.join(DATA_DIR, "quarantine", "quarantine_records.csv")

@st.cache_data
def load_data():
    inv_df = pd.DataFrame()
    quarantine_df = pd.DataFrame()
    
    if os.path.exists(PROCESSED_PATH):
        inv_df = pd.read_csv(PROCESSED_PATH)
    
    if os.path.exists(QUARANTINE_PATH):
        quarantine_df = pd.read_csv(QUARANTINE_PATH)
        
    return inv_df, quarantine_df

inv_df, quarantine_df = load_data()

# Top Level Metrics
total_stock = 0
total_products = 0
total_damaged = 0
quarantine_count = len(quarantine_df)
valid_count = len(inv_df)
quality_score = 0

if not inv_df.empty:
    total_stock = inv_df['effective_stock'].sum()
    total_products = inv_df['product_id'].nunique()
    if 'damaged_qty' in inv_df.columns:
        total_damaged = inv_df['damaged_qty'].sum()
    
total_processed = valid_count + quarantine_count
if total_processed > 0:
    quality_score = (valid_count / total_processed) * 100

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Effective Inventory", f"{total_stock:,.0f}")
with col2:
    st.metric("Active SKUs", total_products)
with col3:
    st.metric("Damaged Units", f"{total_damaged:,.0f}", delta_color="inverse")
with col4:
    st.metric("Quarantined", quarantine_count, delta_color="inverse")
with col5:
    st.metric("Quality Score", f"{quality_score:.1f}%")

st.divider()

# Charts
c1, c2 = st.columns(2)

with c1:
    st.subheader("Inventory Flow (Restock vs Damage)")
    if not inv_df.empty and 'restock_qty' in inv_df.columns and 'damaged_qty' in inv_df.columns:
        flow_data = pd.DataFrame({
            "Type": ["Total Restocked", "Total Damaged"],
            "Units": [inv_df['restock_qty'].sum(), inv_df['damaged_qty'].sum()]
        })
        fig_flow = px.bar(flow_data, x="Type", y="Units", color="Type", 
                          color_discrete_map={"Total Restocked": "blue", "Total Damaged": "orange"})
        st.plotly_chart(fig_flow, use_container_width=True)

with c2:
    st.subheader("Quarantine Reasons")
    if not quarantine_df.empty:
        # Extract base reason (sometimes we might have detailed strings)
        # Just count by 'quarantine_reason'
        reason_counts = quarantine_df['quarantine_reason'].value_counts().reset_index()
        reason_counts.columns = ['Reason', 'Count']
        fig_reasons = px.bar(reason_counts, x="Count", y="Reason", orientation='h', color="Reason")
        st.plotly_chart(fig_reasons, use_container_width=True)
    else:
        st.info("No quarantine records found. Great job!")

# Detailed Views
st.divider()
st.subheader("Inventory Deep Dive")

tab1, tab2 = st.tabs(["Fact Table (Valid)", "Quarantine Ledger"])

with tab1:
    st.dataframe(inv_df, use_container_width=True)

with tab2:
    if not quarantine_df.empty:
        st.dataframe(quarantine_df, use_container_width=True)
        st.caption("These records require manual intervention or rule adjustment.")
    else:
        st.write("No issues.")
