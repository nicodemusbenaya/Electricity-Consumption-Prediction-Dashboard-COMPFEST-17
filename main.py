from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

app = FastAPI()

# Enable CORS for React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML artifacts
print("Loading ML models...")
model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")
feature_names = joblib.load("feature_names.pkl")

# Mapping clusters to specific regions in DKI Jakarta
CLUSTER_COORDS = {
    "cluster_1": (-6.1805, 106.8284), # Jakarta Pusat
    "cluster_2": (-6.2615, 106.8106), # Jakarta Selatan
    "cluster_3": (-6.1683, 106.7588), # Jakarta Barat
    "cluster_4": (-6.2250, 106.9004), # Jakarta Timur
}

def extract_date_features(df):
    df = df.copy()
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["dayofweek"] = df["date"].dt.dayofweek
    df["dayofyear"] = df["date"].dt.dayofyear
    df["weekofyear"] = df["date"].dt.isocalendar().week.astype(int)
    df["quarter"] = df["date"].dt.quarter
    df["is_month_start"] = df["date"].dt.is_month_start.astype(int)
    df["is_month_end"] = df["date"].dt.is_month_end.astype(int)
    df["is_year_start"] = df["date"].dt.is_year_start.astype(int)
    df["is_year_end"] = df["date"].dt.is_year_end.astype(int)
    df["is_weekend"] = (df["date"].dt.dayofweek >= 5).astype(int)
    
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["dow_sin"] = np.sin(2 * np.pi * df["dayofweek"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["dayofweek"] / 7)
    df["doy_sin"] = np.sin(2 * np.pi * df["dayofyear"] / 365)
    df["doy_cos"] = np.cos(2 * np.pi * df["dayofyear"] / 365)
    
    return df

def add_derived_features(df):
    df = df.copy()
    df["temp_range"] = df["temperature_2m_max"] - df["temperature_2m_min"]
    df["apparent_temp_range"] = df["apparent_temperature_max"] - df["apparent_temperature_min"]
    df["temp_diff_max"] = df["temperature_2m_max"] - df["apparent_temperature_max"]
    df["temp_diff_min"] = df["temperature_2m_min"] - df["apparent_temperature_min"]
    
    # Handle missing sunshine duration if any
    sunshine = df.get("sunshine_duration", df.get("daylight_duration", 0))
    df["sunshine_ratio"] = sunshine / (df["daylight_duration"] + 1e-6)
    
    df["wind_gust_ratio"] = df["wind_speed_10m_max"] / (df["wind_gusts_10m_max"] + 1e-6)
    return df

@app.get("/api/forecast")
def get_forecast(cluster: str = Query("cluster_1")):
    if cluster not in CLUSTER_COORDS:
        return {"error": "Invalid cluster"}
        
    lat, lon = CLUSTER_COORDS[cluster]
    
    # Fetch 15 days forecast from Open-Meteo
    url = f"https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,daylight_duration,sunshine_duration,wind_speed_10m_max,wind_gusts_10m_max,shortwave_radiation_sum,et0_fao_evapotranspiration",
        "timezone": "Asia/Jakarta",
        "forecast_days": 15
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {"error": "Failed to fetch weather data"}
        
    data = response.json()
    daily = data.get("daily", {})
    
    if not daily:
        return {"error": "No daily data found"}
        
    # Convert to pandas DataFrame
    df = pd.DataFrame(daily)
    # Open-Meteo uses 'time' for dates
    df = df.rename(columns={"time": "date"})
    df["date"] = pd.to_datetime(df["date"])
    
    # Forward fill missing weather data (e.g. on the 16th day) to prevent temperature dropping to 0
    # Then backward fill, and finally fill remaining with 0 just in case
    df = df.ffill().bfill().fillna(0.0)
    
    # If sunshine_duration is missing from API, mock it with daylight_duration * 0.7
    if "sunshine_duration" not in df.columns or df["sunshine_duration"].isnull().all():
        df["sunshine_duration"] = df["daylight_duration"] * 0.7
        
    # ML Preprocessing
    df_features = df.copy()
    
    # One-Hot Encoding for cluster
    for i in range(1, 5):
        df_features[f"cluster_cluster_{i}"] = (cluster == f"cluster_{i}")
        
    df_features = extract_date_features(df_features)
    df_features = add_derived_features(df_features)
    
    # Select only required features in correct order
    X = pd.DataFrame(index=df_features.index)
    for col in feature_names:
        if col in df_features.columns:
            X[col] = df_features[col]
        else:
            X[col] = 0.0 # Fill missing with 0
            
    # Fill any remaining NaNs with 0 to prevent model crash
    X = X.fillna(0.0)
            
    # Scale and Predict
    X_scaled = scaler.transform(X)
    predictions = model.predict(X_scaled)
    
    # Format Output
    results = []
    for i in range(len(df)):
        results.append({
            "date": df["date"].iloc[i].strftime("%Y-%m-%d"),
            "cluster_id": cluster,
            "electricity_consumption": float(predictions[i]),
            "temperature_2m_max": float(df["temperature_2m_max"].iloc[i]),
            "temperature_2m_min": float(df["temperature_2m_min"].iloc[i]),
            "daylight_duration": float(df["daylight_duration"].iloc[i])
        })
        
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
