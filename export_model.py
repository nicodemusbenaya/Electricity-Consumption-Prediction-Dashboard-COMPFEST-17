import os
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor

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
    
    df = df.drop(columns=["date"])
    return df

def add_derived_features(df):
    df = df.copy()
    df["temp_range"] = df["temperature_2m_max"] - df["temperature_2m_min"]
    df["apparent_temp_range"] = df["apparent_temperature_max"] - df["apparent_temperature_min"]
    df["temp_diff_max"] = df["temperature_2m_max"] - df["apparent_temperature_max"]
    df["temp_diff_min"] = df["temperature_2m_min"] - df["apparent_temperature_min"]
    df["sunshine_ratio"] = df["sunshine_duration"] / (df["daylight_duration"] + 1e-6)
    df["wind_gust_ratio"] = df["wind_speed_10m_max"] / (df["wind_gusts_10m_max"] + 1e-6)
    return df

print("Loading train.csv...")
train_df = pd.read_csv("train.csv")
train_df["date"] = pd.to_datetime(train_df["date"])

y = train_df["electricity_consumption"]
X = train_df.drop(columns=["electricity_consumption"])

# We only have cluster_1 to cluster_4. We can OHE it manually to ensure all columns exist.
X = pd.get_dummies(X, columns=["cluster_id"], prefix="cluster")

# Ensure all 4 clusters exist
for i in range(1, 5):
    col = f"cluster_cluster_{i}"
    if col not in X.columns:
        X[col] = False

X = extract_date_features(X)
X = add_derived_features(X)

X = X.drop(columns=["ID"])

# Save feature names
feature_names = X.columns.tolist()
joblib.dump(feature_names, "feature_names.pkl")

print("Scaling data...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print("Training model (GradientBoostingRegressor)...")
# Let's use GradientBoosting since XGBoost might not be available consistently or requires heavier setup
model = GradientBoostingRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    random_state=42
)
model.fit(X_scaled, y)

print("Saving model and scaler...")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(model, "model.pkl")

print("Model saved successfully!")
