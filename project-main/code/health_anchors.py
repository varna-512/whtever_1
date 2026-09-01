import pandas as pd

health_anchors = pd.DataFrame([
    {
        "city": "Ahmedabad",
        "year": 2010,
        "health_outcome": "All-cause mortality",
        "exposure": "Heat wave",
        "temperature_c": 46.8,
        "effect": 43.1,
        "effect_unit": "percent increase",
        "source": "Azhar et al., 2014",
        "use": "Mortality calibration anchor"
    },
    {
        "city": "Ahmedabad",
        "year": 2010,
        "health_outcome": "Heat-related NICU admissions",
        "exposure": "Daily maximum temperature above 42 C",
        "temperature_c": 42.0,
        "effect": 43.0,
        "effect_unit": "percent increase per 1 C",
        "source": "Basu et al., Ahmedabad heat study",
        "use": "Hospitalization calibration anchor"
    }
])

health_anchors.to_csv(
    "../data/health_anchors.csv",
    index=False
)

print("\nHEALTH ANCHORS:")
print(health_anchors)

print("\nSaved:")
print("../data/health_anchors.csv")