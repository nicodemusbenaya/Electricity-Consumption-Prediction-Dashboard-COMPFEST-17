import pandas as pd
import json

def prepare_data():
    # Read files
    test_df = pd.read_csv('test.csv')
    pred_df = pd.read_csv('submission_improved.csv')
    
    # Merge on ID
    merged = pd.merge(test_df, pred_df, on='ID')
    
    # Extract cluster_id and date separately if needed, but they already exist in test.csv
    # test.csv has 'cluster_id' and 'date' columns
    
    # Keep only relevant columns to minimize payload
    columns_to_keep = [
        'ID', 'cluster_id', 'date', 'electricity_consumption',
        'temperature_2m_max', 'sunshine_duration', 'daylight_duration', 'wind_speed_10m_max'
    ]
    
    final_df = merged[columns_to_keep].copy()
    
    # Sort by cluster_id and date
    final_df = final_df.sort_values(['cluster_id', 'date'])
    
    # Export to JSON
    out_path = 'energy-dashboard/public/data.json'
    
    # Orient='records' gives a list of dictionaries
    records = final_df.to_dict(orient='records')
    
    with open(out_path, 'w') as f:
        json.dump(records, f)
        
    print(f"Successfully generated {out_path} with {len(records)} records.")

if __name__ == '__main__':
    prepare_data()
