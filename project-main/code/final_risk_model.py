import pandas as pd

# Load datasets
heat = pd.read_csv("../data/environmental_risk_dataset.csv")
mortality = pd.read_csv("../data/mortality_risk_dataset.csv")
hospitalization = pd.read_csv("../data/hospitalization_risk_dataset.csv")
vulnerability = pd.read_csv("../data/vulnerability_risk_dataset.csv")

# Make sure dates are in the same format
heat["date"] = pd.to_datetime(heat["date"])
mortality["date"] = pd.to_datetime(mortality["date"])
hospitalization["date"] = pd.to_datetime(hospitalization["date"])

# Keep required health-risk columns
mortality = mortality[["date", "mortality_RR"]]
hospitalization = hospitalization[["date", "hospitalization_RR"]]

# Merge heat + health data
df = heat.merge(mortality, on="date", how="left")
df = df.merge(hospitalization, on="date", how="left")

# Add vulnerability score
vulnerability_score = vulnerability.loc[0, "vulnerability_score"]
df["vulnerability_score"] = vulnerability_score

# Convert health risks into scores
df["mortality_score"] = ((df["mortality_RR"] - 1) / 
                         (df["mortality_RR"].max() - 1)) * 100

df["hospitalization_score"] = ((df["hospitalization_RR"] - 1) /
                               (df["hospitalization_RR"].max() - 1)) * 100

# Fill missing values
df["mortality_score"] = df["mortality_score"].fillna(0)
df["hospitalization_score"] = df["hospitalization_score"].fillna(0)

# Final HEATWISE score
df["final_risk_score"] = (
    0.40 * df["heat_risk_score"]
    + 0.20 * df["mortality_score"]
    + 0.20 * df["hospitalization_score"]
    + 0.20 * df["vulnerability_score"]
)

# Risk category
def risk_category(score):
    if score >= 75:
        return "EXTREME"
    elif score >= 50:
        return "HIGH"
    elif score >= 25:
        return "MODERATE"
    else:
        return "LOW"

df["final_risk_category"] = df["final_risk_score"].apply(risk_category)

# Show highest-risk days
print("\nFINAL HEATWISE RISK MODEL:")
print(
    df.sort_values("final_risk_score", ascending=False)
    [
        [
            "date",
            "Tmax",
            "heat_risk_score",
            "mortality_RR",
            "hospitalization_RR",
            "vulnerability_score",
            "final_risk_score",
            "final_risk_category"
        ]
    ]
    .head(15)
)

# Save final dataset
df.to_csv(
    "../data/final_risk_dataset.csv",
    index=False
)

print("\nFinal risk dataset saved!")
print("../data/final_risk_dataset.csv")