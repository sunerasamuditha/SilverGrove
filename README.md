# SilverGrove

**SilverGrove** is a privacy-first Ambient Assisted Living (AAL) multi-agent platform designed to bridge independent senior living, proactive health monitoring, and secure clinical collaboration using the **Google Agent Development Kit (ADK)** and the **Agent-to-Agent (A2A) protocol**.

---

## Key Features
- **Privacy-by-Design Ambient Monitoring**: Uses camera-free micro-radar / RF sensors to track gait speed, sleep quality, and daily vitals without invasive video surveillance.
- **Proactive Empathy-Driven Companion**: Engages seniors in daily check-ins, orientation questions, and mild cognitive exercises using Gemini 3.1 Flash Lite.
- **Clinical Medication Correlation**: Queries the openFDA drug labeling database and cross-references an embedded clinical reference database to identify dangerous drug side effects and interactions.
- **Secure A2A Alert Routing**: Implements Agent-to-Agent protocol handshakes to exchange health notifications with external Family and Physician agents.
- **HL7 FHIR Interoperability**: Formats vital sign observations as standards-compliant FHIR R4 resources using LOINC codes and UCUM units.

---

## Project Structure
```
SilverGrove/
|-- agents/              # Core ADK Agents
|   |-- sensory_guardian.py
|   |-- cognitive_companion.py
|   |-- medical_compliance.py
|   +-- care_coordinator.py
|-- mcp_servers/         # Model Context Protocol Servers
|   +-- vitals_server.py
|-- tools/               # Agent Tools & Functions
|   |-- vitals_tools.py
|   |-- medication_tools.py
|   |-- alert_tools.py
|   |-- fhir_formatter.py
|   +-- trace_events.py
|-- services/            # GCP Service Layer (Firestore, Pub/Sub)
|   +-- gcp_service.py
|-- data/                # Resident profiles & alert timeline
|   |-- residents.json
|   +-- alerts_timeline.json
|-- static/              # Clinical Dashboard UI
|   |-- index.html
|   |-- index.css
|   |-- index.js
|   |-- a2a-explorer.html
|   +-- infographic.html
|-- a2a/                 # A2A Agent Card definitions
|   +-- agent_cards.py
|-- .github/             # CI/CD Workflows
|   +-- workflows/
|       +-- deploy.yml
|-- .gitignore
|-- agent.py             # Root ADK Orchestrator (4-agent sequential pipeline)
|-- main.py              # FastAPI server + SSE streaming + A2A routes
|-- Dockerfile
+-- .env
```

---

## Architecture

SilverGrove orchestrates 4 specialized agents in a sequential pipeline:

1. **Sensory Guardian** -- Ingests ambient radar telemetry and compares live readings against resident baselines to detect anomalies.
2. **Medical Compliance** -- Cross-references detected anomalies against the resident's active prescriptions using openFDA and the embedded clinical reference database.
3. **Cognitive Companion** -- Translates cold clinical data into warm, empathetic dialogue for the resident.
4. **Care Coordinator** -- Structures the consensus into an A2A-compliant alert payload and dispatches it to family and physician agents.

---

## Running Locally

```bash
# Set your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env

# Install dependencies
pip install google-adk google-genai mcp fastapi uvicorn python-dotenv

# Start the server
python main.py
```

The dashboard will be available at `http://localhost:8180`.
