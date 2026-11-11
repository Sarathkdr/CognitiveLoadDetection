
import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ----------------------------------
# 1. Define project paths
# ----------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

DATASET_PATH = os.path.join(
    BASE_DIR, "dataset", "typing_data.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR, "backend", "model"
)

MODEL_PATH = os.path.join(
    MODEL_DIR, "cognitive_load_model.pkl"
)


# ----------------------------------
# 2. Load dataset
# ----------------------------------

print("\nLoading dataset...")

if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(
        "Dataset not found: " + DATASET_PATH
    )

df = pd.read_csv(DATASET_PATH)

print("\nDataset loaded successfully!")
print(df.head())

print("\nDataset shape:", df.shape)


# ----------------------------------
# 3. Select input features
# ----------------------------------

features = [
    "typing_speed",
    "average_pause",
    "backspace_count",
    "average_key_interval",
    "duration_seconds",
    "total_characters"
]

target = "cognitive_load"


# ----------------------------------
# 4. Validate dataset
# ----------------------------------

required_columns = features + [target]

missing = [
    column for column in required_columns
    if column not in df.columns
]

if missing:
    raise ValueError(
        f"Missing columns: {missing}"
    )

df = df[required_columns].copy()

for column in features:
    df[column] = pd.to_numeric(
        df[column], errors="coerce"
    )

df = df.dropna()

df = df[
    (df[features] >= 0).all(axis=1)
]

df[target] = df[target].astype(str).str.strip().str.title()

df = df[
    df[target].isin(["Low", "Medium", "High"])
]

if df.empty:
    raise ValueError(
        "No valid labelled data found."
    )

print("\nClass distribution:")
print(df[target].value_counts())


# ----------------------------------
# 5. Prepare training data
# ----------------------------------

X = df[features]
y = df[target]

class_counts = y.value_counts()

if len(class_counts) != 3:
    raise ValueError(
        "Dataset must contain Low, Medium and High labels."
    )

if class_counts.min() < 2:
    raise ValueError(
        "Collect at least 2 records for every class."
    )

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ----------------------------------
# 6. Train Random Forest
# ----------------------------------

print("\nTraining Random Forest model...")

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    min_samples_split=2,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)


# ----------------------------------
# 7. Evaluate model
# ----------------------------------

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test, predictions
)

print("\nModel Evaluation")
print("--------------------------")

print("Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        predictions,
        labels=["Low", "Medium", "High"]
    )
)


# ----------------------------------
# 8. Save trained model
# ----------------------------------

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

joblib.dump(model, MODEL_PATH)

print("\nModel saved successfully!")

print("Model location:", MODEL_PATH)

print("\nMachine Learning Training Completed!")
