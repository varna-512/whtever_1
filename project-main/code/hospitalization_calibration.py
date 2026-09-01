import math

# Ahmedabad hospitalization anchor
threshold_temperature = 42.0
risk_increase_per_degree = 43.0

# Relative risk for each 1°C above threshold
RR_per_degree = 1 + (risk_increase_per_degree / 100)

# Convert to exponential coefficient
beta_hosp = math.log(RR_per_degree)

print("HOSPITALIZATION CALIBRATION")
print("---------------------------")
print(f"Threshold temperature : {threshold_temperature} °C")
print(f"Risk increase / °C     : {risk_increase_per_degree}%")
print(f"Relative risk / °C     : {RR_per_degree:.3f}")
print(f"Calibrated beta        : {beta_hosp:.5f}")

# Check
RR_check = math.exp(beta_hosp)

print(f"RR check               : {RR_check:.3f}")
import pandas as pd

# Load environmental dataset
df = pd.read_csv("../data/environmental_risk_dataset.csv")

# Hospitalization parameters
threshold_temperature = 42.0
beta_hosp = 0.35767

# Calculate hospitalization relative risk
df["hospitalization_RR"] = df["Tmax"].apply(
    lambda T: math.exp(beta_hosp * max(0, T - threshold_temperature))
)

df["hospitalization_RR"] = df["hospitalization_RR"].round(3)

print("\nDAILY HOSPITALIZATION RELATIVE RISK:")
print(
    df.sort_values("hospitalization_RR", ascending=False)
    .head(15)[
        ["date", "Tmax", "heat_risk_score",
         "risk_category", "hospitalization_RR"]
    ]
)

# Save
df.to_csv("../data/hospitalization_risk_dataset.csv", index=False)

print("\nSaved:")
print("../data/hospitalization_risk_dataset.csv")