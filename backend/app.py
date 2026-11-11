
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

# Model location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "cognitive_load_model.pkl")

# Features used by the ML model
FEATURES = [
    "typing_speed",
    "average_pause",
    "backspace_count",
    "average_key_interval",
    "duration_seconds",
    "total_characters"
]


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "success",
        "project": "Cognitive Load Detection System",
        "message": "Flask API is running successfully"
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Cognitive Load Detection API"
    })


@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        if not os.path.exists(MODEL_PATH):
            return jsonify({
                "status": "error",
                "message": "ML model not found. Train the model first."
            }), 503

        data = request.get_json(silent=True)

        if not data:
            return jsonify({
                "status": "error",
                "message": "Please provide valid JSON input."
            }), 400

        # Validate required features
        missing = [feature for feature in FEATURES if feature not in data]

        if missing:
            return jsonify({
                "status": "error",
                "message": "Missing required features.",
                "missing_features": missing
            }), 400

        # Prepare input
        input_data = pd.DataFrame(
            [[float(data[feature]) for feature in FEATURES]],
            columns=FEATURES
        )

        # Load trained model
        model = joblib.load(MODEL_PATH)

        # Predict cognitive workload
        prediction = model.predict(input_data)[0]

        return jsonify({
            "status": "success",
            "predicted_cognitive_load": str(prediction),
            "note": "Experimental prediction based on typing behavior, not a medical diagnosis."
        })

    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "Feature values must be numeric."
        }), 400

    except Exception as e:
        app.logger.exception("Prediction failed")
        return jsonify({
            "status": "error",
            "message": "Prediction could not be completed."
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
