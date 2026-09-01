import joblib
import pandas as pd


# --------------------------------------------------
# LOAD TRAINED HEATWISE ML MODEL
# --------------------------------------------------

MODEL_PATH = "../data/heatwise_ml_model.pkl"

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# FEATURES USED BY THE MODEL
# --------------------------------------------------

FEATURES = [
    ...
]


# --------------------------------------------------
# PREDICT HEAT RISK
# --------------------------------------------------

def predict_heat_risk(data):

    # Use the exact feature order stored in the trained model
    features = model.feature_names_in_

    X = data.loc[:, features]

    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    if prediction == 0:
        risk = "LOW/MODERATE"
    else:
        risk = "HIGH/EXTREME"

    confidence = max(probabilities) * 100

    return {
        "risk": risk,
        "confidence": confidence,
        "low_moderate_probability": probabilities[0] * 100,
        "high_extreme_probability": probabilities[1] * 100
    }


# --------------------------------------------------
# TEST WITH LATEST DATA
# --------------------------------------------------

df = pd.read_csv("../data/heatwise_final_dataset.csv")

latest = df.iloc[[-1]]

result = predict_heat_risk(latest)

print("\nHEATWISE PREDICTION ENGINE")
print("--------------------------")

print("Date:", latest.iloc[0]["date"])
print("Predicted Risk:", result["risk"])
print("Confidence: {:.2f}%".format(result["confidence"]))

print(
    "LOW/MODERATE: {:.2f}%".format(
        result["low_moderate_probability"]
    )
)

print(
    "HIGH/EXTREME: {:.2f}%".format(
        result["high_extreme_probability"]
    )
)