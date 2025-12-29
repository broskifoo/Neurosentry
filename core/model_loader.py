# core/model_loader.py
import pandas as pd
import joblib
from pathlib import Path

# Relative paths inside your project
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "baseline_model.joblib"
FEATURES_PATH = BASE_DIR / "features.csv"

def load_model_and_features():
    """
    Loads the trained ML model and expected feature columns.
    If files are missing, it provides clear error messages.
    """
    model = None
    feature_columns = []

    # ----- Load trained AI model -----
    if MODEL_PATH.exists():
        try:
            model = joblib.load(MODEL_PATH)
            print(f"[✅] AI model loaded successfully from: {MODEL_PATH}")
        except Exception as e:
            print(f"[ERROR] Failed to load model ({MODEL_PATH}): {e}")
    else:
        print(f"[⚠️] Model file not found: {MODEL_PATH}")
        print("       → Please run 'train_baseline.py' to train the model first.")

    # ----- Load feature columns -----
    if FEATURES_PATH.exists():
        try:
            df = pd.read_csv(FEATURES_PATH)
            if 'label' in df.columns:
                feature_columns = df.drop('label', axis=1).columns.tolist()
            else:
                feature_columns = df.columns.tolist()
            print(f"[ℹ️] Loaded {len(feature_columns)} feature columns: {feature_columns}")
        except Exception as e:
            print(f"[ERROR] Failed to load features ({FEATURES_PATH}): {e}")
    else:
        print(f"[⚠️] Feature file not found: {FEATURES_PATH}")
        print("       → Please run 'feature_extractor.py' or 'train_baseline.py' first.")

    return model, feature_columns
