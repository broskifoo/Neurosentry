#!/usr/bin/env python3
from __future__ import annotations
import argparse, time, json, sys, os
from pathlib import Path
from collections import Counter, deque
import joblib
import pandas as pd
from core.ai_explainer import explain



# ---------------- DB ----------------
try:
    from core.db import init_db, insert_scan_result
    DB_READY = True
except Exception as e:
    DB_READY = False
    DB_ERR = e

# ---------------- CLI ----------------
ap = argparse.ArgumentParser()
ap.add_argument("--stream", required=True)
ap.add_argument("--window", type=int, default=3)
ap.add_argument("--step", type=int, default=1)
ap.add_argument("--threshold", type=float, default=0.1)
ap.add_argument("--model", default="baseline_model.joblib")
ap.add_argument("--features", default="features_used.txt")
ap.add_argument("--echo", action="store_true")
args = ap.parse_args()

STREAM = Path(args.stream)
MODEL = Path(args.model)
FEATURES = Path(args.features)

# ---------------- Load model ----------------
model = joblib.load(MODEL)
features = [l.strip() for l in FEATURES.read_text().splitlines() if l.strip()]

# ---------------- Init DB ----------------
if DB_READY:
    init_db()
    print("[i] DB logging enabled")
else:
    print("[i] DB logging disabled:", DB_ERR)

# ---------------- Helpers ----------------
def build_row(window):
    c = Counter(window)
    return pd.DataFrame([{f: c.get(f, 0) for f in features}])

def predict_and_log(window):
    df = build_row(window)
    proba_full = model.predict_proba(df)[0]  # Get both probabilities
    prob_benign = float(proba_full[0])  # Class 0 = benign
    prob_malicious = float(proba_full[1])  # Class 1 = malicious
    
    is_malicious = prob_malicious >= args.threshold

    # Generate AI explanation
    ai_result = explain(window)
    
    full_explanation = f"[{ai_result['severity']}] {ai_result['title']}: {ai_result['explanation']}"
    
    # DEBUG: Show both probabilities
    print(f"[ALERT] {'MALICIOUS' if is_malicious else 'benign'}")
    print(f"        Benign: {prob_benign:.3f} | Malicious: {prob_malicious:.3f} | Threshold: {args.threshold}")
    print(f"        {full_explanation}")

    if DB_READY:
        insert_scan_result(
            is_threat=is_malicious,
            confidence=prob_malicious,
            explanation=full_explanation,
            findings={
                "window": list(window),
                "severity": ai_result['severity'],
                "title": ai_result['title'],
                "prob_benign": prob_benign,
                "prob_malicious": prob_malicious
            }
        )



# ---------------- Stream ----------------
buf = deque(maxlen=args.window)

if not STREAM.exists():
    STREAM.write_text("")

with open(STREAM, "r") as f:
    f.seek(0, os.SEEK_END)
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.25)
            continue

        evt = json.loads(line)
        action = evt.get("action")
        if not action:
            continue

        if args.echo:
            print("[evt]", action)

        buf.append(action)
        if len(buf) == args.window:
            predict_and_log(list(buf))
