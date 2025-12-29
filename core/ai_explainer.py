"""
ai_explainer.py — Human-readable threat explanation engine
Deterministic, security-focused (no hallucination).
"""

from typing import List, Dict


def explain(window: List[str]) -> Dict[str, str]:
    explanation = []
    severity = "Low"
    title = "Suspicious Activity Detected"

    unique = set(window)

    # --- Single-event explanations (very important) ---
    if unique == {"process_info"}:
        title = "Process Execution Observed"
        explanation.append(
            "A process execution was observed on the system. "
            "While this is common, unusual or repeated executions may indicate reconnaissance or scripted activity."
        )
        severity = "Low"

    elif unique == {"file_create"}:
        title = "Suspicious File Creation"
        explanation.append(
            "A file was created in a monitored directory. "
            "Malware often drops payloads or temporary files during execution."
        )
        severity = "Medium"

    elif unique == {"persistence_attempt"}:
        title = "Persistence Attempt Detected"
        explanation.append(
            "A write operation to a sensitive system directory was detected. "
            "This behavior is commonly associated with attempts to establish persistence."
        )
        severity = "High"

    # --- Multi-event attack patterns ---
    if "process_info" in unique and "file_create" in unique:
        title = "Payload Dropper Behavior"
        explanation.append(
            "A process execution followed by file creation was observed. "
            "This pattern is commonly associated with malware droppers deploying payloads."
        )
        severity = max(severity, "High", key=_severity_rank)

    if "file_create" in unique and "persistence_attempt" in unique:
        title = "Persistence Mechanism Detected"
        explanation.append(
            "File creation followed by a persistence attempt suggests malware attempting to survive system reboots."
        )
        severity = "High"

    if "network_c2_beacon" in unique:
        title = "Command and Control Activity"
        explanation.append(
            "Outbound network communication consistent with command-and-control behavior was detected."
        )
        severity = "Critical"

    # --- Fallback (rare now) ---
    if not explanation:
        explanation.append(
            "The system detected an unusual sequence of events that deviates from normal behavior."
        )

    return {
        "title": title,
        "severity": severity,
        "explanation": " ".join(explanation),
        "window": " → ".join(window),
    }




def _severity_rank(level: str) -> int:
    return {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}.get(level, 1)
