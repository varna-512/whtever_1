import pandas as pd

# Load final HEATWISE risk dataset
df = pd.read_csv("../data/final_risk_dataset.csv")


# Action recommendation based on risk level
def recommend_action(row):

    risk = row["final_risk_category"]

    if risk == "EXTREME":
        return (
            "Activate extreme heat response; "
            "issue public warning; prioritize vulnerable groups; "
            "increase healthcare readiness"
        )

    elif risk == "HIGH":
        return (
            "Issue heat-health warning; "
            "advise vulnerable groups to reduce heat exposure; "
            "increase health monitoring"
        )

    elif risk == "MODERATE":
        return (
            "Issue preventive heat advisory; "
            "encourage hydration and reduced outdoor exposure"
        )

    else:
        return (
            "Continue routine monitoring and "
            "normal heat-safety awareness"
        )


# Generate recommended action
df["recommended_action"] = df.apply(
    recommend_action,
    axis=1
)


# Display highest-risk days
print("\nHEATWISE ACTION RECOMMENDATIONS:")

print(
    df.sort_values(
        "final_risk_score",
        ascending=False
    )
    [
        [
            "date",
            "Tmax",
            "final_risk_score",
            "final_risk_category",
            "recommended_action"
        ]
    ]
    .head(15)
)


# Save
df.to_csv(
    "../data/heatwise_final_dataset.csv",
    index=False
)

print("\nHEATWISE FINAL DATASET SAVED!")
print("../data/heatwise_final_dataset.csv")