import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import os
import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
# import matplotlib.cm as cm
import matplotlib.colors as mcolors

st.set_page_config( page_title='White-Space Analysis',layout='wide')

# --- PAGE ARCHITECTURE ---
st.title("🎯 White-Space Analysis")
st.subheader("Module 1: Unsupervised Network Expansion Mapping")
st.markdown("---")

# --- Data Loading with Caching ---
@st.cache_data
def load_data():
    internal = pd.read_csv("data/internal_touchpoints.csv")
    customers = pd.read_csv("data/customer_touchpoints.csv")
    history = pd.read_csv("data/historical_performance.csv")
    
    if os.path.exists("data/proposed_ro_locations.csv"):
        proposals = pd.read_csv("data/proposed_ro_locations.csv")
    else:
        proposals = pd.DataFrame()
        
    return internal, customers, history, proposals

@st.cache_data
def load_geo_data():
    territories = gpd.read_file("data/territory_boundaries.geojson")
    state_border = gpd.read_file("data/maharashtra_border.geojson")
    return territories, state_border

internal_df, customer_df, history_df, proposals_df = load_data()
territories_gdf, state_border_gdf = load_geo_data()

# ==============================================================================
# 🎯 NOTEBOOK ALIGNED SPATIAL FILTERING & DBSCAN ENGINE
# ==============================================================================
customers_gdf = gpd.GeoDataFrame(
    customer_df, 
    geometry=gpd.points_from_xy(customer_df['Longitude'], customer_df['Latitude']),
    crs="EPSG:4326"
)

# Isolate unserved workshops based on exact notebook polygon exclusion logic
joined_market = gpd.sjoin(customers_gdf, territories_gdf[['geometry']], how="left", predicate="within")
unserved_customers = joined_market[joined_market['index_right'].isna()].copy()

# Initialize variables
customer_df['Final_Cluster'] = -1
total_clusters = 0
clustered_shops = 0
isolated_noise = len(customer_df)
cluster_colors = {}
final_counts = pd.Series(dtype=int)

if not unserved_customers.empty:
    coords = np.radians(unserved_customers[['Latitude', 'Longitude']])
    
    EARTH_RADIUS_KM = 6371.0
    epsilon_km = 25.0
    min_cluster_size = 15
    epsilon_rad = epsilon_km / EARTH_RADIUS_KM
    
    dbscan = DBSCAN(eps=epsilon_rad, min_samples=min_cluster_size, algorithm='ball_tree', metric='haversine')
    unserved_customers['Cluster_Label'] = dbscan.fit_predict(coords)
    
    # Post-processing point verification rules
    viable_clusters = unserved_customers[unserved_customers['Cluster_Label'] != -1].copy()
    cluster_counts = viable_clusters['Cluster_Label'].value_counts()
    valid_cluster_labels = cluster_counts[cluster_counts >= min_cluster_size].index
    
    viable_clusters = viable_clusters[viable_clusters['Cluster_Label'].isin(valid_cluster_labels)].copy()
    final_counts = viable_clusters['Cluster_Label'].value_counts().sort_index()
    
    # Map verified cluster labels back to primary tracking frame
    cluster_mapping_dict = dict(zip(viable_clusters['ID'], viable_clusters['Cluster_Label']))
    customer_df['Final_Cluster'] = customer_df['ID'].map(cluster_mapping_dict).fillna(-1).astype(int)
    
    total_clusters = len(final_counts)
    clustered_shops = len(viable_clusters)
    isolated_noise = len(customer_df) - clustered_shops

    # Dynamic tab20 Colormap lookup array compilation
    cmap = plt.get_cmap('tab20')
    for idx, cluster_id in enumerate(final_counts.index):
        cluster_colors[cluster_id] = mcolors.rgb2hex(cmap(idx % 20))

# ==============================================================================
# SPATIAL APP LAYOUT & CONTROL PANELS
# ==============================================================================
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### 📊 Whitespace Metrics")
    st.metric("Discovered Expansion Gaps", f"{total_clusters} Zones")
    st.metric("Aggregated Cluster Workshops", f"{clustered_shops:,} Units")
    st.metric("Served / Scattered Noise", f"{isolated_noise:,} Units")
    
    st.markdown("---")
    st.markdown("### 🗺️ Map Controls")
    show_territories = st.checkbox("Show Territory Boundaries", value=True)
    show_internal = st.checkbox("Show Operational Footprint", value=True)
    show_whitespace = st.checkbox("Show Clustered Customer Gaps", value=True)
    
    if not proposals_df.empty:
        show_proposals = st.checkbox("✨ Show Proposed RO Locations", value=True)
    else:
        show_proposals = False
        
    if total_clusters > 0:
        st.markdown("---")
        with st.expander("📍 View Active Cluster Sizes", expanded=True):
            for cluster_id, count in final_counts.items():
                hex_color = cluster_colors[cluster_id]
                st.markdown(
                    f'<span style="color:{hex_color}; font-size:18px;">●</span> '
                    f'<b>Cluster {cluster_id}:</b> {count} workshops', 
                    unsafe_allow_html=True
                )

with col2:
    m = folium.Map(location=[19.0, 75.5], zoom_start=7, tiles="CartoDB positron")
    
    # 1. State Boundary Frame
    folium.GeoJson(
        state_border_gdf, name="Maharashtra Border",
        style_function=lambda feature: {"color": "black", "weight": 4, "fillOpacity": 0}
    ).add_to(m)
    
    # 2. Operational Territory Polygons
    if show_territories:
        folium.GeoJson(
            territories_gdf, name="Territories",
            style_function=lambda feature: {"fillColor": "#3186cc", "color": "black", "weight": 1, "fillOpacity": 0.10},
            tooltip=folium.GeoJsonTooltip(fields=["ID", "Type", "Hub"])
        ).add_to(m)

    # 3. Dynamic Customer Layout Canvas (Renders your exact 9 chromatic footprints)
    if show_whitespace:
        for _, row in customer_df.iterrows():
            c_label = row['Final_Cluster']
            is_valid_cluster = c_label != -1
            
            if is_valid_cluster:
                pt_color = cluster_colors[c_label]
                pt_radius = 5.0
                pt_opacity = 0.85
                pt_weight = 1.0
                popup_msg = f"Validated Whitespace Cluster #{c_label}"
            else:
                pt_color = '#d3d3d3'
                pt_radius = 1.5
                pt_opacity = 0.15
                pt_weight = 0
                popup_msg = "Served Network / Scattered Noise"
            
            folium.CircleMarker(
                location=[row["Latitude"], row["Longitude"]],
                radius=pt_radius, 
                color=pt_color if is_valid_cluster else "none", 
                fill=True, 
                fill_color=pt_color,
                fill_opacity=pt_opacity,
                weight=pt_weight,
                popup=f"<b>{row['Type']}</b><br>{popup_msg}"
            ).add_to(m)

    # 4. Active Supply Footprint Locations
    if show_internal:
        for _, row in internal_df.iterrows():
            touchpoint_type = str(row["Type"])
            if "Mother Warehouse" in touchpoint_type or "MW" in touchpoint_type:
                marker_color = "darkred"
            elif "Additional Warehouse" in touchpoint_type or "AW" in touchpoint_type:
                marker_color = "orange"
            elif "Retail Office" in touchpoint_type or "RO" in touchpoint_type:
                marker_color = "green"
            else:
                marker_color = "blue"
                
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                icon=folium.Icon(color=marker_color, icon="info-sign"),
                popup=f"<b>{row['Type']}</b><br>Hub ID: {row['ID']}"
            ).add_to(m)

    # 5. Layering the Purple Star ML Proposed RO Locations
    if show_proposals and not proposals_df.empty:
        for _, row in proposals_df.iterrows():
            folium.Marker(
                location=[row["Proposed_RO_Lat"], row["Proposed_RO_Lon"]],
                icon=folium.Icon(color="purple", icon="star"),
                popup=f"<b>✨ ML Proposed RO Hub</b><br>Target Cluster Capacity: {row['Target_Customers']} nodes"
            ).add_to(m)

    # 6. Ultra-Compact Scaled Map Legend
    master_legend_html = """
    <div style="position: fixed; bottom: 25px; left: 25px; width: 215px; height: auto;
         background-color: rgba(255, 255, 255, 0.95); z-index:9999; font-size: 11px; font-family: sans-serif;
         line-height: 1.4; border: 1.5px solid grey; border-radius: 5px; padding: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
         <b style="font-size: 11.5px;">Strategic Touchpoint Legend</b><br>
         <hr style="margin: 4px 0; border: 0; border-top: 1px solid #ddd;">
         <i class="fa fa-map-marker" style="color:darkred; width: 14px;"></i> Mother Warehouse (MW)<br>
         <i class="fa fa-map-marker" style="color:orange; width: 14px;"></i> Addl. Warehouse (AW)<br>
         <i class="fa fa-map-marker" style="color:green; width: 14px;"></i> Retail Office (RO)<br>
         <i class="fa fa-map-marker" style="color:blue; width: 14px;"></i> Active Dealer Node<br>
         <i class="fa fa-star" style="color:purple; width: 14px;"></i> <b>ML Proposed RO Hub</b><br>
         <span style="color:#d3d3d3; font-size:12px; width: 14px; display:inline-block; text-align:center;">●</span> Served Market / Noise<br>
         <span style="color:#1f77b4; font-size:12px; width: 14px; display:inline-block; text-align:center;">●</span> <i>9 Clusters (See Sidebar)</i>
    </div>
    """
    m.get_root().html.add_child(folium.Element(master_legend_html))
            
    # FIXED: Replaced explicit width with use_container_width=True to anchor browser painting bugs for good
    st_folium(m, use_container_width=True, height=650, key="maharashtra_dna_whitespace_canvas", returned_objects=[])