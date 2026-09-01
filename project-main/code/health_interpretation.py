import pandas as pd

# Load health impact dataset
df = pd.read_csv("../data/health_impact_dataset.csv")


def interpret_health(row):
    mortality = row["mortality_RR"]
    hospitalization = row["hospitalization_RR"]

    if mortality >= 1.40 or hospitalization >= 3.0:
        return "Very high heat-related health risk"
    elif mortality >= 1.20 or hospitalization >= 2.0:
        return "High heat-related health risk"
    elif mortality > 1.00 or hospitalization > 1.00:
        return "Elevated heat-related health risk"
    else:
        return "Baseline heat-related health risk"


df["health_interpretation"] = df.apply(
    interpret_health,
    axis=1
)

print("\nHEALTH INTERPRETATION:")
print(
    df.sort_values(
        "mortality_RR",
        ascending=False
    ).head(15)[
        [
            "date",
            "Tmax",
            "mortality_RR",
            "hospitalization_RR",
            "health_interpretation"
        ]
    ]
)

# Save
df.to_csv(
    "../data/health_impact_dataset.csv",
    index=False
)

print("\nUpdated:")
print("../data/health_impact_dataset.csv")