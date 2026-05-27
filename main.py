import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Ensure parent directory is in path for easy importing
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import SilverGroveOrchestrator
from tools.vitals_tools import get_resident_vitals, get_resident_details
from tools.alert_tools import get_alerts_timeline, clear_alerts_timeline

# Initialize FastAPI App
app = FastAPI(
    title="SilverGrove AAL Portal",
    description="Privacy-First Ambient Assisted Living Multi-Agent System Dashboard Gateway",
    version="1.0.0"
)

# Enable CORS for external dashboard client integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Orchestrator instance
orchestrator = SilverGroveOrchestrator()

# Endpoint: List all resident profiles
@app.get("/api/residents")
def list_residents():
    try:
        from mcp_servers.vitals_server import load_residents
        residents = load_residents()
        # Clean up to return array
        res_list = []
        for rid, data in residents.items():
            res_list.append({
                "id": rid,
                "name": data.get("name"),
                "age": data.get("age"),
                "conditions": data.get("conditions"),
                "medications_count": len(data.get("medications", []))
            })
        return res_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint: Get full details & vitals of a resident
@app.get("/api/residents/{resident_id}")
def get_resident_profile(resident_id: str):
    profile = get_resident_details(resident_id)
    if "error" in profile:
        raise HTTPException(status_code=404, detail=profile["error"])
        
    vitals_data = get_resident_vitals(resident_id)
    return {
        "profile": profile,
        "vitals": vitals_data
    }

# Endpoint: Trigger End-to-End Multi-Agent Health Check
@app.post("/api/residents/{resident_id}/check")
def trigger_agent_check(resident_id: str):
    try:
        trajectory = orchestrator.run_health_check(resident_id)
        return trajectory
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint: Retrieve Active A2A Alerts Timeline
@app.get("/api/alerts")
def get_alerts():
    return get_alerts_timeline()

# Endpoint: Reset Alert Log for fresh demo
@app.post("/api/alerts/clear")
def clear_alerts():
    clear_alerts_timeline()
    return {"status": "success", "message": "Alert timeline cleared successfully."}

# Serve High-Fidelity UI Static Files
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8180, reload=True)
