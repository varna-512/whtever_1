from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os
import pickle

app = Flask(__name__)
CORS(app)


# ==================================================
# PATHS
# ==================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "heatwise_final_dataset.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "data",
    "heatwise_ml_model.pkl"
)


# ==================================================
# LOAD DATASET
# ==================================================

df = pd.read_csv(DATA_PATH)

print("\n===================================")
print("HEATWISE BACKEND")
print("===================================")
print("Dataset loaded successfully")
print("Rows:", len(df))
print("Columns:", list(df.columns))


# ==================================================
# LOAD MACHINE LEARNING MODEL
# ==================================================

model = None

try:
    import joblib

    model = joblib.load(MODEL_PATH)

    print("ML model loaded successfully with joblib")

except Exception as joblib_error:

    try:
        with open(MODEL_PATH, "rb") as file:
            model = pickle.load(file)

        print("ML model loaded successfully with pickle")

    except Exception as pickle_error:

        model = None

        print("ML model could not be loaded")
        print("joblib:", joblib_error)
        print("pickle:", pickle_error)


# ==================================================
# HELPER
# ==================================================

def get_value(row, column, default=0):

    if column not in df.columns:
        return default

    value = row[column]

    if pd.isna(value):
        return default

    try:
        return float(value)
    except (ValueError, TypeError):
        return str(value)


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    return jsonify({
        "message": "HEATWISE Backend is running!"
    })


# ==================================================
# SYSTEM STATUS
# ==================================================

@app.route("/api/status")
def status():

    return jsonify({
        "status": "online",
        "system": "HEATWISE",
        "dataset_rows": len(df),
        "ml_model_loaded": model is not None
    })


# ==================================================
# LATEST DATA
# ==================================================

@app.route("/api/latest")
def latest():

    row = df.iloc[-1]

    data = {

        # ------------------------------------------
        # BASIC
        # ------------------------------------------

        "date": str(row["date"]),


        # ------------------------------------------
        # ENVIRONMENT
        # ------------------------------------------

        "temperature": get_value(row, "Tmax"),

        "tmean": get_value(row, "Tmean"),

        "rh_mean": get_value(row, "RH_mean"),

        "hi_max": get_value(row, "HI_max"),

        "wbgt_max": get_value(row, "WBGT_max"),


        # ------------------------------------------
        # HEAT
        # ------------------------------------------

        "heat_severity": get_value(
            row,
            "heat_severity",
            "Low"
        ),

        "heat_risk_score": get_value(
            row,
            "heat_risk_score"
        ),

        "heat_index_score": get_value(
            row,
            "heat_index_score"
        ),

        "heat_streak": get_value(
            row,
            "heat_streak"
        ),


        # ------------------------------------------
        # HEALTH
        # ------------------------------------------

        "mortality_rr": get_value(
            row,
            "mortality_RR",
            1
        ),

        "mortality_score": get_value(
            row,
            "mortality_score"
        ),

        "hospitalization_rr": get_value(
            row,
            "hospitalization_RR",
            1
        ),

        "hospitalization_score": get_value(
            row,
            "hospitalization_score"
        ),


        # ------------------------------------------
        # VULNERABILITY
        # ------------------------------------------

        "vulnerability_score": get_value(
            row,
            "vulnerability_score"
        ),


        # ------------------------------------------
        # FINAL RISK
        # ------------------------------------------

        "final_risk_score": get_value(
            row,
            "final_risk_score"
        ),

        "final_risk_category": str(
            row.get(
                "final_risk_category",
                "LOW"
            )
        ),


        # ------------------------------------------
        # ACTION
        # ------------------------------------------

        "recommended_action": str(
            row.get(
                "recommended_action",
                "Continue routine monitoring."
            )
        )
    }

    return jsonify(data)


# ==================================================
# MACHINE LEARNING PREDICTION
# ==================================================

@app.route("/api/prediction")
def prediction():

    if model is None:

        return jsonify({
            "error": "ML model is not loaded"
        }), 500


    # Latest row
    row = df.iloc[-1]


    try:

        # ------------------------------------------
        # GET FEATURES USED DURING MODEL TRAINING
        # ------------------------------------------

        features = list(model.feature_names_in_)


        # ------------------------------------------
        # CREATE MODEL INPUT
        # ------------------------------------------

        X = pd.DataFrame(
            [[row[feature] for feature in features]],
            columns=features
        )


        # ------------------------------------------
        # PREDICTION
        # ------------------------------------------

        predicted_class = model.predict(X)[0]


        # ------------------------------------------
        # PROBABILITY
        # ------------------------------------------

        probabilities = model.predict_proba(X)[0]

        confidence = float(
            max(probabilities) * 100
        )


        low_probability = float(
            probabilities[0] * 100
        )

        high_probability = float(
            probabilities[1] * 100
        )


        # ------------------------------------------
        # RISK LABEL
        # ------------------------------------------

        if predicted_class == 0:

            risk = "LOW / MODERATE"

        else:

            risk = "HIGH / EXTREME"


        return jsonify({

            "date": str(row["date"]),

            "predicted_risk": risk,

            "prediction_class": int(predicted_class),

            "confidence": round(
                confidence,
                2
            ),

            "low_moderate_probability": round(
                low_probability,
                2
            ),

            "high_extreme_probability": round(
                high_probability,
                2
            ),

            "model": "Random Forest"

        })


    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500
    # ==================================================
# 5-DAY PROTOTYPE FORECAST
# ==================================================

@app.route("/api/forecast")
def forecast():

    if model is None:
        return jsonify({
            "error": "ML model is not loaded"
        }), 500

    try:

        # --------------------------------------------------
        # MODEL FEATURES
        # --------------------------------------------------

        features = list(model.feature_names_in_)

        # --------------------------------------------------
        # USE LAST 5 AVAILABLE DAYS
        #
        # The model was trained to predict TOMORROW'S risk.
        # Therefore each row predicts the following day.
        #
        # This is a historical walk-forward prototype,
        # not a live weather forecast.
        # --------------------------------------------------

        forecast_rows = df.iloc[-6:-1].copy()

        predictions = []

        for _, row in forecast_rows.iterrows():

            # ----------------------------------------------
            # CREATE MODEL INPUT
            # ----------------------------------------------

            X = pd.DataFrame(
                [[row[feature] for feature in features]],
                columns=features
            )

            # ----------------------------------------------
            # PREDICT NEXT DAY
            # ----------------------------------------------

            predicted_class = int(
                model.predict(X)[0]
            )

            # ----------------------------------------------
            # PROBABILITIES
            # ----------------------------------------------

            probabilities = model.predict_proba(X)[0]

            class_probabilities = {
                int(cls): float(prob)
                for cls, prob
                in zip(model.classes_, probabilities)
            }

            low_moderate_probability = (
                class_probabilities.get(0, 0) * 100
            )

            high_extreme_probability = (
                class_probabilities.get(1, 0) * 100
            )

            confidence = max(
                low_moderate_probability,
                high_extreme_probability
            )

            # ----------------------------------------------
            # RISK LABEL
            # ----------------------------------------------

            if predicted_class == 0:
                predicted_risk = "LOW / MODERATE"
            else:
                predicted_risk = "HIGH / EXTREME"

            # ----------------------------------------------
            # NEXT DAY
            # ----------------------------------------------

            source_date = pd.to_datetime(
                row["date"]
            )

            forecast_date = (
                source_date +
                pd.Timedelta(days=1)
            )

            # ----------------------------------------------
            # ADD RESULT
            # ----------------------------------------------

            predictions.append({

                "source_date":
                    source_date.strftime("%Y-%m-%d"),

                "forecast_date":
                    forecast_date.strftime("%Y-%m-%d"),

                "predicted_risk":
                    predicted_risk,

                "prediction_class":
                    predicted_class,

                "confidence":
                    round(confidence, 2),

                "low_moderate_probability":
                    round(
                        low_moderate_probability,
                        2
                    ),

                "high_extreme_probability":
                    round(
                        high_extreme_probability,
                        2
                    )
            })

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return jsonify({

            "system": "HEATWISE",

            "forecast_type":
                "Historical Walk-Forward Prototype",

            "model":
                "Random Forest",

            "prediction_horizon":
                "5 days",

            "latest_available_date":
                str(
                    pd.to_datetime(
                        df["date"].iloc[-1]
                    ).strftime("%Y-%m-%d")
                ),

            "predictions":
                predictions
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# ==================================================
# RUN SERVER
# ==================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )
