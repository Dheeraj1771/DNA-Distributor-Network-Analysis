import streamlit as st
import pandas as pd

# --- PAGE ARCHITECTURE ---
st.set_page_config( page_title='DNA - Distributor Network Analysis',layout='wide')

# Custom CSS for consistent executive styling across pages
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
    .executive-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #3186cc;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .step-header {
        color: #1f77b4;
        font-weight: bold;
    }
    
    /* MOBILE RESPONSIVE & ANTI-CLIPPING KPI CARD OVERRIDES */
    .dna-metric-card {
        background-color: #ffffff;
        padding: 14px;
        border-radius: 6px;
        border: 1px solid #e6e9ef;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .dna-metric-label {
        font-size: 12.5px;
        color: #555555;
        font-weight: 500;
        line-height: 1.3;
        margin-bottom: 6px;
        white-space: normal; /* Forces text to wrap instead of cutting off */
        word-wrap: break-word;
    }
    .dna-metric-value {
        font-size: 19px;
        color: #111111;
        font-weight: 700;
        white-space: normal; /* Prevents values like (5x5 km) from getting clipped */
        word-wrap: break-word;
    }
    @media (max-width: 768px) {
        .dna-metric-value { font-size: 16px; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧬 DNA - Distributor Network Analysis Platform")
st.subheader("State Focus: Maharashtra (Executive Enterprise Interface)")
st.markdown("---")

st.markdown("""
### 📌 Project Overview
The **Distributor Network Analysis (DNA)** platform is an enterprise-grade spatial intelligence tool designed to solve a critical commercial challenge: **How do we efficiently scale our distribution footprint across Maharashtra without blindly deploying high-cap infrastructure?**

By feeding internal asset logs, customer touchpoints, and regional vehicle populations into dual machine learning pipelines, DNA replaces intuition with mathematical certainty.
""")

st.markdown("### 🛠️ Core Analytical Objectives")

col_obj1, col_obj2 = st.columns(2)
with col_obj1:
    st.markdown("""
    <div class="executive-card">
        <h4 class="step-header">🎯 1. Unsupervised Whitespace Mapping</h4>
        <p><b>The Goal:</b> Scan the entire state geography to discover localized clusters of unserved independent workshops falling completely outside our existing sales territories.</p>
        <p><b>The Science:</b> Implements spatial density clustering (DBSCAN) tracking coordinates in radians to group pockets containing at least 15 shops within a strict 25km radius window.</p>
    </div>
    """, unsafe_allow_html=True)
    
with col_obj2:
    st.markdown("""
    <div class="executive-card">
        <h4 class="step-header">💰 2. Supervised Econometric Scaling</h4>
        <p><b>The Goal:</b> Extract exactly how much revenue a single active vehicle and independent mechanic generate for our hubs, then score all 12,800+ grids in the state.</p>
        <p><b>The Science:</b> Constrained Linear Regression modeling learns fixed operational parameter weights from current active operations to calculate regional financial potential maps.</p>
    </div>
    """, unsafe_allow_html=True)

# --- BASELINE KPI METRICS ---
st.markdown("### 📊 Maharashtra Baseline Metrics and Network Overview")
try:
    customer_df = pd.read_csv("data/customer_touchpoints.csv")
    history_df = pd.read_csv("data/historical_performance.csv")
    internal_df = pd.read_csv("data/internal_touchpoints.csv")
    total_rev = history_df["Revenue_INR"].sum() / 10000000 
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown("""
            <div class="dna-metric-card">
                <div class="dna-metric-label">Total Regional Mesh Blocks</div>
                <div class="dna-metric-value">12,847 Cells (5x5 km)</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
            <div class="dna-metric-card">
                <div class="dna-metric-label">Total Active Customers</div>
                <div class="dna-metric-value">{len(customer_df):,}</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
            <div class="dna-metric-card">
                <div class="dna-metric-label">Total Historical Revenue Baseline</div>
                <div class="dna-metric-value">₹{total_rev:.2f} Cr</div>
            </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
            <div class="dna-metric-card">
                <div class="dna-metric-label">Total Internal Touchpoints</div>
                <div class="dna-metric-value">{len(internal_df)} Nodes <span style="font-size:11px; color:#666; font-weight:normal;">(MW, AW, RO, Dealer)</span></div>
            </div>
        """, unsafe_allow_html=True)
    
except Exception:
    st.warning("Ensure database CSV items exist within the data directory to view live system summaries.")