import pandas as pd
import math

# Load environmental dataset
df = pd.read_csv("../data/environmental_risk_dataset.csv")

# Calibrated mortality parameters
MMT = 28.0
beta = 0.01906

# Calculate relative mortality risk
df["mortality_RR"] = df["Tmax"].apply(
    lambda T: math.exp(beta * max(0, T - MMT))
)

# Round for readability
df["mortality_RR"] = df["mortality_RR"].round(3)

print("\nDAILY MORTALITY RELATIVE RISK:")
print(
    df.sort_values("mortality_RR", ascending=False)
    .head(15)[
        ["date", "Tmax", "heat_risk_score", "risk_category", "mortality_RR"]
    ]
)

# Save
df.to_csv("../data/mortality_risk_dataset.csv", index=False)

print("\nSaved:")
print("../data/mortality_risk_dataset.csv")