import os
import json
import datetime
from typing import Dict, Any

# Path to alerts log
DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALERTS_PATH = os.path.join(DATA_DIR, "data", "alerts_timeline.json")

def initialize_alerts_file():
    """Ensure data directory and alerts log exist."""
    os.makedirs(os.path.dirname(ALERTS_PATH), exist_ok=True)
    if not os.path.exists(ALERTS_PATH):
        with open(ALERTS_PATH, "w") as f:
            json.dump([], f)

def log_alert_to_timeline(resident_id: str, resident_name: str, severity: str, message: str, actions: list, correlation: str = None) -> dict:
    """
    Format a structured health alert, log it to the alerts timeline, and return the alert dictionary.
    """
    initialize_alerts_file()
    
    alert = {
        "id": f"alert_{int(datetime.datetime.utcnow().timestamp())}",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "resident_id": resident_id,
        "resident_name": resident_name,
        "severity": severity.upper(), # INFO, ADVISORY, WARNING, CRITICAL
        "message": message,
        "actions": actions,
        "correlation": correlation,
        "acknowledged": False
    }
    
    try:
        with open(ALERTS_PATH, "r+") as f:
            data = json.load(f)
            data.insert(0, alert)  # Newest first
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except Exception:
        # If read/write fails, try to overwrite
        with open(ALERTS_PATH, "w") as f:
            json.dump([alert], f, indent=2)
            
    return alert

def get_alerts_timeline() -> list:
    """Retrieve all logged alerts from the timeline."""
    initialize_alerts_file()
    try:
        with open(ALERTS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return []

def clear_alerts_timeline():
    """Clear all alerts for a fresh simulation run."""
    os.makedirs(os.path.dirname(ALERTS_PATH), exist_ok=True)
    with open(ALERTS_PATH, "w") as f:
        json.dump([], f)

if __name__ == "__main__":
    clear_alerts_timeline()
    log_alert_to_timeline(
        resident_id="martha_001",
        resident_name="Martha Reynolds",
        severity="WARNING",
        message="Gait speed decline of 15.3% detected over 5 days (0.85 m/s down to 0.72 m/s). Elevated blood pressure of 142/88 mmHg.",
        actions=["Check on Martha immediately", "Advise her to drink water and stand slowly", "Request primary care physician medication review"],
        correlation="Recently started Metoprolol Succinate 50mg (Beta-blocker) on 2026-05-23. Common side effects include orthostatic hypotension and bradycardia."
    )
    print(get_alerts_timeline())
