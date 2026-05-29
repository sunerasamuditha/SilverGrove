import os
import json
import datetime
from typing import Dict, Any, List
from services.gcp_service import get_alerts_db, save_alert_db, clear_alerts_db, publish_alert_event

def log_alert_to_timeline(resident_id: str, resident_name: str, severity: str, message: str, actions: list, correlation: str = None) -> dict:
    """
    Format a structured health alert, log it to Firestore (or local timeline),
    publish it over Cloud Pub/Sub, and return the alert dictionary.
    Strictly emoji-free logs.
    """
    # Create timestamp
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    
    alert = {
        "id": f"alert_{int(datetime.datetime.utcnow().timestamp())}",
        "timestamp": timestamp,
        "resident_id": resident_id,
        "resident_name": resident_name,
        "severity": severity.upper(), # INFO, ADVISORY, WARNING, CRITICAL
        "message": message,
        "actions": actions,
        "correlation": correlation,
        "acknowledged": False
    }
    
    # Persist alert in Firestore / file
    save_alert_db(alert)
    
    # Broadcast event via Pub/Sub
    publish_alert_event(alert)
            
    return alert

def get_alerts_timeline() -> list:
    """Retrieve all logged alerts from the timeline."""
    return get_alerts_db()

def clear_alerts_timeline():
    """Clear all alerts for a fresh simulation run."""
    clear_alerts_db()

if __name__ == "__main__":
    clear_alerts_timeline()
    log_alert_to_timeline(
        resident_id="martha_001",
        resident_name="Martha Reynolds",
        severity="WARNING",
        message="Gait speed decline of 15.3% detected over 5 days. Elevated blood pressure of 142/88 mmHg.",
        actions=["Check on Martha immediately", "Advise her to drink water and stand slowly", "Request primary care physician medication review"],
        correlation="Recently started Metoprolol Succinate 50mg (Beta-blocker) on 2026-05-23. Common side effects include orthostatic hypotension."
    )
    print(get_alerts_timeline())
