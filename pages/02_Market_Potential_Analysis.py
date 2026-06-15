import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import os
import numpy as np
from folium.utilities import JsCode 

# --- MUST BE THE ABSOLUTE FIRST STREAMLIT COMMAND TO AVOID CONTAINMENT BUGS ---
st.set_page_config(page_title='Market Potential Engine', layout='wide')

# --- PAGE HERO HEADERS ---
st.title("💰 Market Potential Engine")
st.subheader("Module 2: Supervised Econometric Scaling & Expansion Simulation")
st.markdown("---")

# --- Data Loading with Caching ---
@st.cache_data
def load_market_data():
    internal = pd.read_csv("data/internal_touchpoints.csv")
    state_border = gpd.read_file("data/maharashtra_border.geojson")
    
    if os.path.exists("data/market_potential_predictions.csv"):
        predictions = pd.read_csv("data/market_potential_predictions.csv")
        
        # Convert predictions to a GeoDataFrame using center coordinates
        predictions_gdf = gpd.GeoDataFrame(
            predictions,
            geometry=gpd.points_from_xy(predictions['Center_Lon'], predictions['Center_Lat']),
            crs="EPSG:4326"
        )
        
        # Keep ONLY the grid cells that fall inside the true state border polygon
        clipped_gdf = gpd.sjoin(predictions_gdf, state_border[['geometry']], how="inner", predicate="within")
        
        if 'index_right' in clipped_gdf.columns:
            clipped_gdf = clipped_gdf.drop(columns=['index_right'])
        predictions = pd.DataFrame(clipped_gdf.drop(columns='geometry'))
    else:
        predictions = pd.DataFrame()
        
    return internal, state_border, predictions

internal_df, state_border_gdf, predictions_df = load_market_data()

# ==============================================================================
# 🤖 ML ENGINE CORE PARAMETERS & PRE-PROCESSING
# ==============================================================================
COEF_VEHICLE = 4740.27
COEF_WORKSHOP = 312154.76
INTERCEPT = 11448494.60

if predictions_df.empty:
    st.error("⚠️ 'market_potential_predictions.csv' not found. Please run your Model Ingestion notebook to export predictions.")
    st.stop()

# Isolate "Off-Grid" targets (Untapped sectors with NO active dealers)
off_grid_df = predictions_df[predictions_df['Is_Active_Dealer'] == 0].copy()

# Sort descending to pull out the true Top 5 Highest Paying Expansion Targets INSIDE Maharashtra
top_5_off_grid = off_grid_df.sort_values(by='Predicted_Potential_Revenue', ascending=False).head(5)
top_5_ids = top_5_off_grid['Grid_ID'].tolist()

# Define physical bounding dimensions strictly for the top 5 highlighted grid box outlines
GRID_BOX_DELTA = 0.022

# ==============================================================================
# SPATIAL APP LAYOUT & SIDEBAR METRICS
# ==============================================================================
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### 🏆 Top 5 Untapped Grids")
    
    selected_grid_id = st.selectbox(
        "Select High-Value Grid to Inspect:",
        top_5_ids,
        index=0
    )
    
    grid_profile = top_5_off_grid[top_5_off_grid['Grid_ID'] == selected_grid_id].iloc[0]
    v_base = int(grid_profile['Active_Vehicles'])
    w_base = int(grid_profile['Workshop_Count'])
    rev_base = float(grid_profile['Predicted_Potential_Revenue'])
    
    st.markdown("---")
    st.markdown("### 🎛️ Revenue Simulator")
    st.caption("Prescriptive simulation using trained ML parameter weights.")
    
    added_w = st.slider("Deploy Strategic Partner Workshops:", min_value=0, max_value=10, value=3, step=1)
    
    simulated_w_total = w_base + added_w
    simulated_rev = INTERCEPT + (v_base * COEF_VEHICLE) + (simulated_w_total * COEF_WORKSHOP)
    net_uplift = simulated_rev - rev_base
    
    st.markdown(f"**Grid `{selected_grid_id}` Current Parameters:**")
    st.write(f"🚗 Reg. Vehicles: **{v_base:,} units**")
    st.write(f"🛠️ Active Independent Shops: **{w_base} nodes**")
    st.write(f"💸 Baseline Revenue Yield: **₹{rev_base/10000000:.2f} Cr**")
    
    st.success(f"### 🚀 Projected Net ROI Uplift:\n ## ₹{net_uplift:,.2f}")
    st.info(f"New Simulated Grid Scale Target: **₹{simulated_rev/10000000:.2f} Cr**")

with col2:
    m = folium.Map(location=[19.0, 75.5], zoom_start=7, tiles="CartoDB positron")
    
    # 1. State Boundary Line Layer
    folium.GeoJson(
        state_border_gdf, name="Maharashtra Border",
        style_function=lambda feature: {"color": "black", "weight": 4, "fillOpacity": 0}
    ).add_to(m)
    
    show_dealers = st.checkbox("Show Active Operational Dealer Anchors", value=True)
    
    # ==============================================================================
    # ⚡ HIGH-PERFORMANCE GEOJSON POINT MATRIX (FIXED VIA JSCODE SERIALIZATION)
    # ==============================================================================
    features = []
    for _, row in predictions_df.iterrows():
        g_id = row['Grid_ID']
        lat, lon = row['Center_Lat'], row['Center_Lon']
        rev = row['Predicted_Potential_Revenue']
        veh = row['Active_Vehicles']
        wrk = row['Workshop_Count']
        is_active = int(row['Is_Active_Dealer'])
        
        is_top_5 = g_id in top_5_ids
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "Grid_ID": g_id,
                "Revenue": f"₹{rev/10000000:.2f} Cr",
                "Vehicles": f"{int(veh):,}",
                "Workshops": int(wrk),
                "Status": "🏆 Top 5 Target" if is_top_5 else ("Active Footprint" if is_active == 1 else "Untapped Gaps"),
                "is_top_5": is_top_5,
                "is_active": is_active
            }
        }
        features.append(feature)
        
    mesh_geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # FIXED: Wrapped raw logic inside JsCode execution tags to prevent standard Python serialization failure
    point_to_layer_js = JsCode("""
    function(feature, latlng) {
        var props = feature.properties;
        if (props.is_top_5) {
            return L.circleMarker(latlng, {
                radius: 6.5,
                fillColor: "#FF4500",
                color: "#FFD700",
                weight: 1.5,
                fillOpacity: 0.95
            });
        } else if (props.is_active === 1) {
            return L.circleMarker(latlng, {
                radius: 3.5,
                fillColor: "#3186cc",
                color: "#3186cc",
                weight: 0,
                fillOpacity: 0.55
            });
        } else {
            return L.circleMarker(latlng, {
                radius: 2.5,
                fillColor: "#2ca02c",
                color: "#2ca02c",
                weight: 0,
                fillOpacity: 0.30
            });
        }
    }
    """)
            
    # Inject the high-performance mesh layout point matrix with hover cards attached
    folium.GeoJson(
        mesh_geojson,
        name="Maharashtra Market Topography Grid",
        point_to_layer=point_to_layer_js,
        tooltip=folium.GeoJsonTooltip(
            fields=["Grid_ID", "Status", "Revenue", "Vehicles", "Workshops"],
            aliases=["Grid ID:", "Status:", "Potential Revenue:", "Active Vehicles:", "Workshop Density:"],
            localize=True,
            sticky=True
        )
    ).add_to(m)

    # ==============================================================================
    # 🏆 HIGHLIGHTED LAYER BOUNDS FOR THE TOP 5 HIGHEST PAYING EXPANSION CELLS
    # ==============================================================================
    for rank, (_, row) in enumerate(top_5_off_grid.iterrows(), 1):
        lat, lon = row['Center_Lat'], row['Center_Lon']
        grid_id = row['Grid_ID']
        potential_rev = row['Predicted_Potential_Revenue']
        
        bounds = [[lat - GRID_BOX_DELTA, lon - GRID_BOX_DELTA], [lat + GRID_BOX_DELTA, lon + GRID_BOX_DELTA]]
        is_active_selection = (grid_id == selected_grid_id)
        
        box_color = "#FFD700" if is_active_selection else "#FF4500"
        box_weight = 3.5 if is_active_selection else 2.0
        
        folium.Rectangle(
            bounds=bounds,
            color=box_color,
            weight=box_weight,
            fill=True,
            fill_color=box_color,
            fill_opacity=0.25 if is_active_selection else 0.12,
            popup=f"<b>🏆 RANK {rank} TARGET BOX: {grid_id}</b><br>Potential Revenue: ₹{potential_rev/10000000:.2f} Cr"
        ).add_to(m)

    # Draw marker for currently selected drop-down grid coordinate item
    selected_profile = predictions_df[predictions_df['Grid_ID'] == selected_grid_id].iloc[0]
    folium.Marker(
        location=[selected_profile['Center_Lat'], selected_profile['Center_Lon']],
        icon=folium.Icon(color="red", icon="star", prefix="fa"),
        popup=f"<b>Inspecting Cell ID: {selected_grid_id}</b>"
    ).add_to(m)

    if show_dealers:
        for _, row in internal_df.iterrows():
            if str(row["Type"]) == "Dealer":
                folium.CircleMarker(
                    location=[row["Latitude"], row["Longitude"]],
                    radius=4, color="blue", fill=True, fill_color="blue", fill_opacity=0.7,
                    popup=f"Active Dealer: {row['ID']}"
                ).add_to(m)

    # Overlap-Proof Scale Map Legend
    master_legend_html = """
    <div style="position: fixed; bottom: 25px; left: 25px; width: 225px; height: auto;
         background-color: rgba(255, 255, 255, 0.95); z-index:9999; font-size: 11px; font-family: sans-serif;
         line-height: 1.4; border: 1.5px solid grey; border-radius: 5px; padding: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
         <b style="font-size: 11.5px;">Potential Engine Legend</b><br>
         <hr style="margin: 4px 0; border: 0; border-top: 1px solid #ddd;">
         <span style="color:#FFD700; font-size:14px;">●</span> <b>Top 5 Untapped Goldmines</b><br>
         <span style="color:#2ca02c; font-size:14px;">●</span> Untapped Expansion Grid Box<br>
         <span style="color:#3186cc; font-size:14px;">●</span> Active Operating Grid Box<br>
         <span style="color:blue; font-size:12px;">●</span> Active Existing Dealer Node<br>
         <i class="fa fa-star" style="color:red; font-size:10px;"></i> Active Inspector Target
    </div>
    """
    m.get_root().html.add_child(folium.Element(master_legend_html))
            
    st_folium(m, use_container_width=True, height=650, key="maharashtra_dna_potential_canvas", returned_objects=[])