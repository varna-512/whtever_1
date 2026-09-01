import pandas as pd

file_path = "../data/open-meteo-23.02N72.60E53m.csv"

df = pd.read_csv(file_path, skiprows=2)
df["time"] = pd.to_datetime(df["time"], utc=True)

df["time_ist"] = df["time"].dt.tz_convert("Asia/Kolkata")

print(df[["time", "time_ist"]].head())
df["date"] = df["time_ist"].dt.date
print(df[["time_ist", "date"]].head())
df = df.rename(columns={
    "temperature_2m (°C)": "temperature",
    "relative_humidity_2m (%)": "humidity",
    "dew_point_2m (°C)": "dew_point",
    "wind_speed_10m (km/h)": "wind_speed",
    "shortwave_radiation_instant (W/m²)": "solar_radiation"
})

print(df.columns.tolist())
print("\nDaily dataset:")

import matplotlib.pyplot as plt

first_week = df[df["date"] <= df["date"].iloc[0] + pd.Timedelta(days=6)]

plt.figure(figsize=(12, 5))
plt.plot(first_week["time_ist"], first_week["temperature"])
plt.xlabel("Time")
plt.ylabel("Temperature (°C)")
plt.title("Ahmedabad Temperature — First 7 Days")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
daily = df.groupby("date").agg(
    Tmax=("temperature", "max"),
    Tmin=("temperature", "min"),
    Tmean=("temperature", "mean"),
    RH_mean=("humidity", "mean"),
    RH_max=("humidity", "max"),
    wind_mean=("wind_speed", "mean"),
    wind_max=("wind_speed", "max"),
    solar_mean=("solar_radiation", "mean"),
    solar_max=("solar_radiation", "max"),
).reset_index()
daily.to_csv("../data/ahmedabad_daily_weather.csv", index=False)

print("\nDaily dataset:")
print(daily.head())

print("\nDaily shape:")
print(daily.shape)
hottest_days = daily.sort_values("Tmax", ascending=False).head(10)

print("\nTop 10 hottest days:")
print(hottest_days[["date", "Tmax", "Tmin", "Tmean", "RH_mean"]])
import numpy as np

def calculate_heat_index(temp_c, humidity):
    temp_f = temp_c * 9 / 5 + 32

    hi_f = (
        -42.379
        + 2.04901523 * temp_f
        + 10.14333127 * humidity
        - 0.22475541 * temp_f * humidity
        - 0.00683783 * temp_f**2
        - 0.05481717 * humidity**2
        + 0.00122874 * temp_f**2 * humidity
        + 0.00085282 * temp_f * humidity**2
        - 0.00000199 * temp_f**2 * humidity**2
    )

    return (hi_f - 32) * 5 / 9


daily["heat_index"] = calculate_heat_index(
    daily["Tmax"],
    daily["RH_mean"]
)

print("\nHottest days with Heat Index:")
print(
    daily.sort_values("Tmax", ascending=False)
    .head(10)[["date", "Tmax", "RH_mean", "heat_index"]]
)
df["heat_index"] = calculate_heat_index(
    df["temperature"],
    df["humidity"]
)

daily_hi = df.groupby("date")["heat_index"].max().reset_index()

daily_hi = daily_hi.rename(
    columns={"heat_index": "HI_max"}
)

daily = daily.merge(daily_hi, on="date")

print("\nDaily maximum Heat Index:")
print(
    daily.sort_values("HI_max", ascending=False)
    .head(10)[["date", "Tmax", "RH_mean", "HI_max"]]
)
daily.to_csv("../data/ahmedabad_heat_features.csv", index=False)

print("\nHeat-feature dataset saved!")
# ---------------- WBGT CALCULATION ----------------

def calculate_wbgt(temp_c, humidity, solar_radiation, wind_speed):
    # Approximate wet-bulb temperature using Stull formula
    tw = (
        temp_c * np.arctan(0.151977 * np.sqrt(humidity + 8.313659))
        + np.arctan(temp_c + humidity)
        - np.arctan(humidity - 1.676331)
        + 0.00391838 * humidity**1.5
        * np.arctan(0.023101 * humidity)
        - 4.686035
    )

    # Approximate globe temperature
    tg = (
        temp_c
        + 0.02 * solar_radiation
        - 0.5 * wind_speed
    )

    # Outdoor WBGT approximation
    wbgt = (
        0.7 * tw
        + 0.2 * tg
        + 0.1 * temp_c
    )

    return wbgt


# Calculate hourly WBGT
df["wbgt"] = calculate_wbgt(
    df["temperature"],
    df["humidity"],
    df["solar_radiation"],
    df["wind_speed"]
)

# Maximum WBGT for each day
daily_wbgt = df.groupby("date")["wbgt"].max().reset_index()

daily_wbgt = daily_wbgt.rename(
    columns={"wbgt": "WBGT_max"}
)

daily = daily.merge(daily_wbgt, on="date")

print("\nDaily maximum WBGT:")
print(
    daily.sort_values("WBGT_max", ascending=False)
    .head(10)[
        ["date", "Tmax", "RH_mean", "HI_max", "WBGT_max"]
    ]
)
daily.to_csv("../data/ahmedabad_wbgt_features.csv", index=False)

print("\nWBGT-feature dataset saved!")
# ---------------- HEAT SEVERITY SCORE ----------------

daily["heat_severity"] = (
    0.4 * daily["HI_max"]
    + 0.6 * daily["WBGT_max"]
)

print("\nHeat Severity Score:")
print(
    daily.sort_values("heat_severity", ascending=False)
    .head(10)[
        ["date", "Tmax", "HI_max", "WBGT_max", "heat_severity"]
    ]
)
# ---------------- TEMPERATURE SEVERITY ----------------

def temperature_score(t):
    if t < 30:
        return 0
    elif t < 35:
        return 25
    elif t < 40:
        return 50
    elif t < 45:
        return 75
    elif t < 47:
        return 90
    else:
        return 100


daily["temperature_score"] = daily["Tmax"].apply(temperature_score)

print("\nTemperature Severity:")
print(
    daily.sort_values("temperature_score", ascending=False)
    .head(10)[
        ["date", "Tmax", "temperature_score"]
    ]
)
# ---------------- HEAT INDEX SEVERITY ----------------

def heat_index_score(hi):
    if hi < 32:
        return 0
    elif hi < 38:
        return 25
    elif hi < 43:
        return 50
    elif hi < 48:
        return 75
    elif hi < 54:
        return 90
    else:
        return 100


daily["heat_index_score"] = daily["HI_max"].apply(heat_index_score)

print("\nHeat Index Severity:")
print(
    daily.sort_values("heat_index_score", ascending=False)
    .head(10)[
        ["date", "HI_max", "heat_index_score"]
    ]
)
# ---------------- WBGT SEVERITY ----------------

def wbgt_score(wbgt):
    if wbgt < 25:
        return 0
    elif wbgt < 28:
        return 25
    elif wbgt < 31:
        return 50
    elif wbgt < 34:
        return 75
    elif wbgt < 37:
        return 90
    else:
        return 100


daily["wbgt_score"] = daily["WBGT_max"].apply(wbgt_score)

print("\nWBGT Severity:")
print(
    daily.sort_values("wbgt_score", ascending=False)
    .head(10)[
        ["date", "WBGT_max", "wbgt_score"]
    ]
)
# ---------------- FINAL HEAT RISK SCORE ----------------

daily["heat_risk_score"] = (
    0.30 * daily["temperature_score"]
    + 0.30 * daily["heat_index_score"]
    + 0.40 * daily["wbgt_score"]
)

print("\nFINAL HEAT RISK SCORE:")
print(
    daily.sort_values("heat_risk_score", ascending=False)
    .head(15)[
        [
            "date",
            "Tmax",
            "HI_max",
            "WBGT_max",
            "temperature_score",
            "heat_index_score",
            "wbgt_score",
            "heat_risk_score"
        ]
    ]
)
# ---------------- RISK CATEGORY ----------------

def risk_category(score):
    if score < 25:
        return "LOW"
    elif score < 50:
        return "MODERATE"
    elif score < 75:
        return "HIGH"
    else:
        return "EXTREME"


daily["risk_category"] = daily["heat_risk_score"].apply(risk_category)

print("\nHEATWISE RISK LEVEL:")
print(
    daily.sort_values("heat_risk_score", ascending=False)
    .head(15)[
        ["date", "heat_risk_score", "risk_category"]
    ]
)
# ---------------- HEAT PERSISTENCE ----------------

daily = daily.sort_values("date").reset_index(drop=True)

daily["extreme_day"] = daily["heat_risk_score"] >= 75

daily["heat_streak"] = (
    daily["extreme_day"]
    .groupby(
        (~daily["extreme_day"]).cumsum()
    )
    .cumsum()
)

print("\nHEAT PERSISTENCE:")
print(
    daily[daily["heat_streak"] > 0]
    .sort_values("heat_streak", ascending=False)
    .head(20)[
        ["date", "heat_risk_score", "risk_category", "heat_streak"]
    ]
)
# ---------------- FINAL ENVIRONMENTAL DATASET ----------------

environmental_data = daily[
    [
        "date",
        "Tmax",
        "Tmean",
        "RH_mean",
        "HI_max",
        "WBGT_max",
        "heat_severity",
        "temperature_score",
        "heat_index_score",
        "wbgt_score",
        "heat_risk_score",
        "risk_category",
        "heat_streak"
    ]
].copy()

environmental_data.to_csv(
    "../data/environmental_risk_dataset.csv",
    index=False
)

print("\nFINAL ENVIRONMENTAL DATASET:")
print(environmental_data.head())

print("\nShape:")
print(environmental_data.shape)

print("\nSaved as:")
print("../data/environmental_risk_dataset.csv")