#!/usr/bin/env python3
# Baseline classifier training for NeuroSentry
# - expects features.csv with a 'label' column (0 benign, 1 malicious)
# - saves: baseline_model.joblib, metrics.txt, features_used.txt

from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, roc_auc_score
)
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent
FEATURES_CSV = PROJECT_ROOT / "features.csv"
MODEL_PATH   = PROJECT_ROOT / "baseline_model.joblib"
METRICS_PATH = PROJECT_ROOT / "metrics.txt"
FEATURES_OUT = PROJECT_ROOT / "features_used.txt"
RANDOM_STATE = 42

def main():
    print(f"Loading feature set: {FEATURES_CSV}")
    if not FEATURES_CSV.exists():
        print("[ERROR] features.csv not found. Run your feature_extractor first.")
        return

    df = pd.read_csv(FEATURES_CSV)
    if "label" not in df.columns:
        print("[ERROR] 'label' column missing in features.csv")
        return

    print(f"Loaded {len(df)} rows, {len(df.columns)-1} features (+ label).")

    # X = features, y = labels
    y = df["label"].astype(int)
    X = df.drop(columns=["label"])

    # Save the exact feature order the model expects
    FEATURES_OUT.write_text("\n".join(X.columns) + "\n", encoding="utf-8")

    # Stratified split keeps class balance in train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=RANDOM_STATE, stratify=y if y.nunique() > 1 else None
    )

    print(f"Training on {len(X_train)} rows, testing on {len(X_test)} rows.")

    # Robust baseline: handles imbalance; reproducible
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        n_jobs=-1,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )

    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm  = confusion_matrix(y_test, y_pred)

    # Some datasets are tiny; protect AUC computation
    try:
        y_proba = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_proba)
    except Exception:
        y_proba, auc = None, None

    report = classification_report(y_test, y_pred, digits=3)

    # Persist model
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved → {MODEL_PATH}")

    # Persist metrics
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        f.write(f"Rows: {len(df)}\n")
        f.write(f"Train: {len(X_train)}  Test: {len(X_test)}\n\n")
        f.write(f"Accuracy: {acc:.4f}\n")
        if auc is not None:
            f.write(f"ROC AUC: {auc:.4f}\n")
        f.write("\nClassification Report:\n")
        f.write(report)
        f.write("\nConfusion Matrix:\n")
        f.write(np.array2string(cm))
        f.write("\n")
    print(f"Metrics saved → {METRICS_PATH}")
    print("\n--- Summary ---")
    print(f"Accuracy: {acc*100:.2f}%")
    if auc is not None:
        print(f"ROC AUC: {auc:.3f}")
    print("Confusion matrix:\n", cm)
    print("\nFeature order written to:", FEATURES_OUT)

if __name__ == "__main__":
    main()
