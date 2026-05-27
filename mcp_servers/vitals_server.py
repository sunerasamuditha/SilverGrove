import os
import json
from mcp.server.fastmcp import FastMCP

# Initialize MCP Server
mcp = FastMCP("SilverGroveVitalsServer")

# Path to residents database
DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESIDENTS_PATH = os.path.join(DATA_DIR, "data", "residents.json")

# Simulated sensor readings in real-time
# Martha has: elevated BP (142/88 vs 130/80) and gait slowdown (0.72 vs 0.85, ~15.3% drop)
# Arthur has: stable vitals but slightly low sleep hours
SIMULATED_TELEMETRY = {
    "martha_001": {
        "heart_rate_bpm": 78,
        "bp_systolic": 142,
        "bp_diastolic": 88,
        "gait_speed_ms": 0.72,
        "sleep_hours": 5.4,
        "room_occupancy": "bedroom",
        "timestamp": "2026-05-27T22:00:00Z"
    },
    "arthur_002": {
        "heart_rate_bpm": 69,
        "bp_systolic": 122,
        "bp_diastolic": 75,
        "gait_speed_ms": 0.64,
        "sleep_hours": 6.2,
        "room_occupancy": "living_room",
        "timestamp": "2026-05-27T22:00:00Z"
    }
}

# Gait history trend for the past 5 days
GAIT_HISTORY = {
    "martha_001": [0.85, 0.82, 0.79, 0.75, 0.72],  # Declining trend!
    "arthur_002": [0.65, 0.64, 0.65, 0.63, 0.64]   # Stable trend!
}

def load_residents():
    try:
        with open(RESIDENTS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}

@mcp.tool()
def get_resident_details(resident_id: str) -> dict:
    """Retrieve full details of a resident (name, age, active conditions, medications)."""
    residents = load_residents()
    return residents.get(resident_id, {"error": f"Resident {resident_id} not found."})

@mcp.tool()
def get_resident_vitals(resident_id: str) -> dict:
    """Retrieve real-time camera-free vital signs and sensory telemetry from ambient radar sensors."""
    vitals = SIMULATED_TELEMETRY.get(resident_id)
    if not vitals:
        return {"error": f"No vital telemetry available for resident {resident_id}."}
    
    residents = load_residents()
    profile = residents.get(resident_id, {})
    baselines = profile.get("baselines", {})
    
    # Calculate percentage change for critical metrics
    gait_speed = vitals["gait_speed_ms"]
    gait_baseline = baselines.get("gait_speed_ms", 1.0)
    gait_change = ((gait_speed - gait_baseline) / gait_baseline) * 100
    
    bp_sys = vitals["bp_systolic"]
    bp_sys_baseline = baselines.get("bp_systolic", 120)
    bp_sys_change = ((bp_sys - bp_sys_baseline) / bp_sys_baseline) * 100
    
    return {
        "resident_name": profile.get("name", "Unknown"),
        "telemetry": vitals,
        "baselines": baselines,
        "gait_change_percent": round(gait_change, 1),
        "bp_systolic_change_percent": round(bp_sys_change, 1),
        "status": "ANOMALY_DETECTED" if abs(gait_change) >= 15.0 or bp_sys >= 140 else "NORMAL"
    }

@mcp.tool()
def get_gait_trend(resident_id: str) -> dict:
    """Get historical 5-day gait speed trend in m/s for gait degradation analysis."""
    history = GAIT_HISTORY.get(resident_id)
    if not history:
        return {"error": f"No historical gait data for resident {resident_id}."}
    
    change_pct = ((history[-1] - history[0]) / history[0]) * 100
    return {
        "resident_id": resident_id,
        "gait_speed_history_ms": history,
        "total_gait_change_percent": round(change_pct, 1),
        "verdict": "DEGRADATION_DETECTED" if change_pct <= -15.0 else "STABLE"
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
