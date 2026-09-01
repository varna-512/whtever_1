import pandas as pd

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

df = pd.read_csv("../data/heatwise_final_dataset.csv")

df["date"] = pd.to_datetime(df["date"])


# --------------------------------------------------
# 2. CREATE TOMORROW'S TARGET
# --------------------------------------------------

df["tomorrow_risk"] = df["final_risk_category"].shift(-1)

df = df.dropna(subset=["tomorrow_risk"])


# 1 = HIGH or EXTREME tomorrow
# 0 = LOW or MODERATE tomorrow

df["target"] = df["tomorrow_risk"].isin(
    ["HIGH", "EXTREME"]
).astype(int)


# --------------------------------------------------
# 3. SELECT FEATURES
# --------------------------------------------------

features = [
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
    "heat_streak",
    "mortality_RR",
    "hospitalization_RR",
    "vulnerability_score"
]

X = df[features]
y = df["target"]


# --------------------------------------------------
# 4. TRAIN / TEST SPLIT
# --------------------------------------------------
# --------------------------------------------------
# 4. TIME-BASED TRAIN / TEST SPLIT
# --------------------------------------------------

# First 80% = training
# Last 20% = testing
split_index = int(len(X) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print("\nTRAINING DATA:", X_train.shape)
print("TEST DATA:", X_test.shape)



print("\nTRAINING DATA:", X_train.shape)
print("TEST DATA:", X_test.shape)


# --------------------------------------------------
# 5. TRAIN RANDOM FOREST
# --------------------------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)


# --------------------------------------------------
# 6. PREDICTIONS
# --------------------------------------------------

y_pred = model.predict(X_test)


# --------------------------------------------------
# 7. MODEL PERFORMANCE
# --------------------------------------------------

print("\nMODEL PERFORMANCE")
print("------------------")

print("\nAccuracy:")
print(accuracy_score(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    target_names=["LOW/MODERATE", "HIGH/EXTREME"]
))


# --------------------------------------------------
# 8. FEATURE IMPORTANCE
# --------------------------------------------------

importance = pd.DataFrame({
    "feature": features,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print("\nFEATURE IMPORTANCE")
print("------------------")
print(importance)


# --------------------------------------------------
# 9. PREDICT LATEST AVAILABLE DAY
# --------------------------------------------------

latest_row = X.iloc[[-1]]

latest_date = df.iloc[-1]["date"]

prediction = model.predict(latest_row)[0]
probabilities = model.predict_proba(latest_row)[0]

# Convert prediction into readable risk category
if prediction == 0:
    predicted_risk = "LOW/MODERATE"
else:
    predicted_risk = "HIGH/EXTREME"

confidence = max(probabilities) * 100

print("\nHEATWISE ML PREDICTION")
print("----------------------")
print("Date:", latest_date)
print("Predicted Risk:", predicted_risk)
print("Confidence: {:.2f}%".format(confidence))

print("\nProbability:")
print("LOW/MODERATE: {:.2f}%".format(probabilities[0] * 100))
print("HIGH/EXTREME: {:.2f}%".format(probabilities[1] * 100))

print("\nHEATWISE ML MODEL TRAINED SUCCESSFULLY!")
# --------------------------------------------------
# 10. SAVE TRAINED MODEL
# --------------------------------------------------

joblib.dump(model, "../data/heatwise_ml_model.pkl")

print("\nML MODEL SAVED!")
print("../data/heatwise_ml_model.pkl")