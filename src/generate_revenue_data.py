import os
import pandas as pd
import numpy as np

print("Generating dedicated Revenue Analysis dataset for Maharashtra...")
# FIX: Corrected 'ok=True' to 'exist_ok=True'
os.makedirs('../data', exist_ok=True)

np.random.seed(101) # Unique seed for this specific analysis

total_grids = 12847
grid_ids = [f"G_{i:05d}" for i in range(1, total_grids + 1)]

# Establish the 12,847 geographic grids across Maharashtra
latitudes = np.random.uniform(16.0, 21.5, size=total_grids)
longitudes = np.random.uniform(73.0, 80.0, size=total_grids)

revenue_data = pd.DataFrame({
    'Grid_ID': grid_ids,
    'Center_Lat': latitudes,
    'Center_Lon': longitudes,
    'Active_Vehicles': 0,
    'Workshop_Count': 0,
    'Historical_Revenue': 0.0,
    'Is_Active_Dealer': 0
})

# 1. Inject 30 Active Dealerships with flawless economic relationships
print("Seeding 30 operational dealer grids with realistic metrics...")
active_indices = np.random.choice(revenue_data.index, size=30, replace=False)

for idx in active_indices:
    vehicles = np.random.randint(6000, 24000)
    # Workshops scale naturally as a function of vehicle density
    workshops = int(vehicles / np.random.randint(700, 1100)) + np.random.randint(3, 6)
    
    # Economics: Base 1.2Cr + (₹4,800 per Vehicle) + (₹240,000 per Workshop) + noise
    base_rev = 12000000 + (vehicles * 4800) + (workshops * 240000)
    noise = base_rev * np.random.uniform(-0.02, 0.02)
    
    revenue_data.loc[idx, 'Active_Vehicles'] = vehicles
    revenue_data.loc[idx, 'Workshop_Count'] = workshops
    revenue_data.loc[idx, 'Historical_Revenue'] = round(base_rev + noise, 2)
    revenue_data.loc[idx, 'Is_Active_Dealer'] = 1

# 2. Populate 2,000 Untapped Market Grids (The revenue potential targets)
print("Seeding untapped market potentials...")
empty_indices = revenue_data[revenue_data['Is_Active_Dealer'] == 0].index
untapped_indices = np.random.choice(empty_indices, size=2000, replace=False)

for idx in untapped_indices:
    v_untapped = np.random.randint(4000, 20000)
    w_untapped = int(v_untapped / np.random.randint(800, 1200)) + np.random.randint(1, 4)
    
    revenue_data.loc[idx, 'Active_Vehicles'] = v_untapped
    revenue_data.loc[idx, 'Workshop_Count'] = w_untapped
    # Historical revenue stays 0.0 because no dealer is established here yet!

# Save to a completely new file
output_file = 'data/maharashtra_revenue_grid_data.csv'
revenue_data.to_csv(output_file, index=False)
print(f"✅ Dedicated Revenue Dataset created at: {output_file}")