# src/generate_all_data.py
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import os

print("🚀 Initializing complete spatial data generation for Maharashtra...")

# Set seed for exact reproducibility across runs
np.random.seed(42)
os.makedirs("data", exist_ok=True)

# --- 1. Fetch True State Boundary (Point-in-Polygon Mask) ---
print("Downloading India State Boundaries & Extracting Maharashtra...")
url = "https://raw.githubusercontent.com/india-in-data/india-states-2019/master/india_states.geojson"
gdf_india = gpd.read_file(url)

# Filter explicitly for Maharashtra and save the border for the UI
gdf_mh = gdf_india[gdf_india['ST_NM'].str.upper() == 'MAHARASHTRA']
gdf_mh.to_file("data/maharashtra_border.geojson", driver="GeoJSON")

# Extract the raw geometry polygon to test our coordinates against
mh_polygon = gdf_mh.geometry.iloc[0]

# --- 2. Define Hubs & Spatial Distribution Rules ---
HUBS = {
    "Mumbai": {"lat": 19.0760, "lon": 72.8777, "weight": 0.25},
    "Pune": {"lat": 18.5204, "lon": 73.8567, "weight": 0.15},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882, "weight": 0.10},
    "Nashik": {"lat": 19.9975, "lon": 73.7898, "weight": 0.10},
    "Aurangabad": {"lat": 19.8762, "lon": 75.3433, "weight": 0.05},
    "Kolhapur": {"lat": 16.7050, "lon": 74.2433, "weight": 0.05},
    "Solapur": {"lat": 17.6599, "lon": 75.9064, "weight": 0.05},
    "Amravati": {"lat": 20.9320, "lon": 77.7523, "weight": 0.05}
}

def generate_points_in_polygon(num_points, spread=0.15, polygon=None):
    """Generates coordinates strictly confined within the provided geographic polygon."""
    lats, lons, cities = [], [], []
    minx, miny, maxx, maxy = polygon.bounds
    
    # Generate Hub clusters (80% of data)
    for city, info in HUBS.items():
        count = int(num_points * info["weight"])
        added = 0
        while added < count:
            lat = np.random.normal(info["lat"], spread)
            lon = np.random.normal(info["lon"], spread)
            if polygon.contains(Point(lon, lat)):
                lats.append(lat)
                lons.append(lon)
                cities.append(city)
                added += 1
                
    # Generate Statewide Scatter (20% of data)
    statewide_count = num_points - len(lats)
    added = 0
    while added < statewide_count:
        lat = np.random.uniform(miny, maxy)
        lon = np.random.uniform(minx, maxx)
        if polygon.contains(Point(lon, lat)):
            lats.append(lat)
            lons.append(lon)
            cities.append("Rest of State")
            added += 1
            
    return lats, lons, cities

# --- REQUIREMENT 1: Geocoded Master Data (With Hierarchy) ---
print("Generating Geocoded Master Data & Supply Chain Hierarchy...")

# Force exact infrastructure counts to mimic reality (Total 50 nodes)
internal_types = (["Mother Warehouse (MW)"] * 2 + 
                  ["Additional Warehouse (AW)"] * 5 + 
                  ["Retail Office (RO)"] * 13 + 
                  ["Dealer"] * 30)

int_lats, int_lons, int_cities = generate_points_in_polygon(50, spread=0.1, polygon=mh_polygon)

internal_df = pd.DataFrame({
    "ID": [f"INT_{i:03d}" for i in range(50)],
    "Type": internal_types,
    "Latitude": int_lats,
    "Longitude": int_lons,
    "Hub": int_cities,
    "Coverage_Radius_KM": [100]*2 + [50]*5 + [25]*13 + [15]*30 # MWs have largest coverage, Dealers smallest
})

# Map the Supply Chain Hierarchy (Child nodes pull from Parent nodes)
mws = internal_df[internal_df["Type"] == "Mother Warehouse (MW)"]["ID"].tolist()
aws = internal_df[internal_df["Type"] == "Additional Warehouse (AW)"]["ID"].tolist()

parent_ids = []
for t in internal_df["Type"]:
    if t == "Mother Warehouse (MW)":
        parent_ids.append("HQ_NATIONAL")
    elif t == "Additional Warehouse (AW)":
        parent_ids.append(np.random.choice(mws)) # AWs pull stock strictly from MWs
    else:
        parent_ids.append(np.random.choice(aws + mws)) # ROs & Dealers pull from AWs or MWs

internal_df["Parent_Node_ID"] = parent_ids
internal_df.to_csv("data/internal_touchpoints.csv", index=False)

# Generate Customer/Independent Workshop Data
cust_lats, cust_lons, cust_cities = generate_points_in_polygon(1500, spread=0.25, polygon=mh_polygon)
customer_df = pd.DataFrame({
    "ID": [f"CUST_{i:04d}" for i in range(1500)],
    "Type": np.random.choice(["Independent Workshop", "Trader", "MASS", "Fleet Owner"], size=1500, p=[0.6, 0.15, 0.15, 0.1]),
    "Latitude": cust_lats, 
    "Longitude": cust_lons, 
    "Hub": cust_cities
})
customer_df.to_csv("data/customer_touchpoints.csv", index=False)


# --- REQUIREMENT 2: Historical Performance Data ---
print("Generating Historical Performance Data (3 Years)...")
dates = pd.date_range(start="2023-01-01", periods=36, freq="ME")
historical_records = []

# Only Dealers process frontline volume in this model
for dealer_id in internal_df[internal_df["Type"] == "Dealer"]["ID"].tolist():
    base_sales = np.random.randint(500000, 2000000)
    for date in dates:
        historical_records.append({
            "Touchpoint_ID": dealer_id, 
            "Date": date.strftime("%Y-%m-%d"),
            "Parts_Volume": int(base_sales / 500) + np.random.randint(-50, 100),
            "Revenue_INR": base_sales + np.random.randint(-100000, 200000)
        })
pd.DataFrame(historical_records).to_csv("data/historical_performance.csv", index=False)


# --- REQUIREMENT 3: Market / Vehicle Parc Data ---
print("Generating Market Demand & Vehicle Parc Data...")
vp_lats, vp_lons, vp_cities = generate_points_in_polygon(2000, spread=0.3, polygon=mh_polygon)
pd.DataFrame({
    "Grid_ID": [f"GRID_{i:04d}" for i in range(2000)],
    "Vehicle_Type": np.random.choice(["Commercial", "Passenger", "Two-Wheeler"], size=2000, p=[0.2, 0.5, 0.3]),
    "Active_Vehicles": np.random.randint(500, 5000, size=2000),
    "Latitude": vp_lats, 
    "Longitude": vp_lons
}).to_csv("data/vehicle_parc.csv", index=False)


# --- REQUIREMENT 4: Current Territory Logic (Polygons) ---
print("Generating Territory Boundaries (GeoJSON)...")

# Filter to only map boundary polygons for frontline sellers (Dealers and ROs)
territory_df = internal_df[internal_df["Type"].isin(["Retail Office (RO)", "Dealer"])].copy()

# Create standard GPS points
geometry = [Point(xy) for xy in zip(territory_df["Longitude"], territory_df["Latitude"])]
gdf_points = gpd.GeoDataFrame(territory_df, geometry=geometry, crs="EPSG:4326")

# Project to Web Mercator (EPSG:3857) to handle global meter-based projections without rigid UTM zone boundaries
gdf_projected = gdf_points.to_crs(epsg=3857)

# Apply distance buffer in meters. Mathematically adjust for Mercator distortion using the cosine of the local latitude.
gdf_projected["geometry"] = gdf_projected.apply(
    lambda row: row.geometry.buffer((row["Coverage_Radius_KM"] * 1000) / np.cos(np.radians(row["Latitude"]))), axis=1
)

# Project perfectly aligned polygons back to standard Lat/Long (EPSG:4326) and Save
gdf_territories = gdf_projected.to_crs(epsg=4326)
gdf_territories[["ID", "Type", "Hub", "geometry"]].to_file("data/territory_boundaries.geojson", driver="GeoJSON")

print("✅ Success! All data generated, strictly masked, and hierarchically linked.")