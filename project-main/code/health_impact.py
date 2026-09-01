import pandas as pd

# Load both health-risk datasets
mortality = pd.read_csv("../data/mortality_risk_dataset.csv")
hospitalization = pd.read_csv("../data/hospitalization_risk_dataset.csv")

# Keep only the columns we need
mortality = mortality[
    ["date", "Tmax", "heat_risk_score", "risk_category", "mortality_RR"]
]

hospitalization = hospitalization[
    ["date", "hospitalization_RR"]
]

# Combine using date
health = mortality.merge(
    hospitalization,
    on="date",
    how="left"
)

print("\nHEALTH IMPACT DATASET:")
print(health.head(15))

print("\nShape:")
print(health.shape)

# Save
health.to_csv("../data/health_impact_dataset.csv", index=False)

print("\nSaved:")
print("../data/health_impact_dataset.csv")