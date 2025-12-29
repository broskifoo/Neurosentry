# main.py
import uvicorn
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# --- Import our refactored logic ---
from core.model_loader import load_model_and_features
from core.ai_explainer import explain
from core.log_parser import parse_sysmon_log, logs_to_features, LogEntry

# --- Pydantic Models for API Requests ---
class ExplainRequest(BaseModel):
    term: str

class AnalysisRequest(BaseModel):
    logs: List[LogEntry]

# --- FastAPI App Initialization ---
app = FastAPI(title="NeuroSentry API")

# --- Add CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load Models on Startup ---
# This code runs once when the server starts
model, feature_columns = load_model_and_features()

# --- API Endpoints ---

@app.get("/")
def read_root():
    """Root endpoint to check if the server is alive."""
    return {"message": "NeuroSentry API is running."}

@app.post("/scan")
async def scan_system_logs():
    """
    Scans Sysmon logs, extracts actions AND locations, analyzes them, 
    and returns detailed results.
    """
    if model is None or not feature_columns:
        return JSONResponse(status_code=503, content={"error": "Model or features not loaded. Cannot scan."})

    print("Initiating system log scan (Sysmon)...")
    extracted_events = parse_sysmon_log() # Reads Sysmon log

    if not extracted_events:
        return JSONResponse(status_code=404, content={"error": "Could not extract any relevant Sysmon actions."})

    try:
        log_entries_for_ml = [LogEntry(action=event["action"]) for event in extracted_events]
        feature_vector = logs_to_features(log_entries_for_ml, feature_columns)
        
        prediction = model.predict(feature_vector)[0]
        probability = model.predict_proba(feature_vector)[0][1]
        
        threat_findings = []
        if prediction == 1:
            explanation_text = f"Threat detected in recent system logs with {probability * 100:.0f}% confidence."
            is_threat = True
            for event in extracted_events:
                action = event["action"]
                if action in ["persistence_attempt", "network_c2_beacon", "file_create"]:
                    threat_findings.append({
                        "action": action,
                        "location": event.get("location", "N/A"),
                        "severity": "CRITICAL" if action in ["persistence_attempt", "network_c2_beacon"] else "HIGH"
                    })
        else:
            explanation_text = f"Scan complete. No threat detected with {(1 - probability) * 100:.0f}% confidence."
            is_threat = False

        return {
            "is_threat": is_threat,
            "confidence": f"{probability:.2f}",
            "explanation": explanation_text,
            "total_events_found": len(extracted_events),
            "threat_findings": threat_findings
        }
    except Exception as e:
        print(f"[ERROR] Error during scan analysis: {e}")
        return JSONResponse(status_code=500, content={"error": "An internal error occurred during scan analysis."})

@app.post("/explain_term")
async def explain_cybersecurity_term(request: ExplainRequest):
    """Uses Google Gemini AI to explain a cybersecurity term."""
    # This function just passes the request to our AI explainer logic
    return await get_ai_explanation(request.term)

# --- Run the Server ---
if __name__ == "__main__":
    print("Starting FastAPI server at http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)