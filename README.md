# SilverGrove A2A

**SilverGrove** is a premium, privacy-first Ambient Assisted Living (AAL) multi-agent platform designed to bridge independent senior living, proactive health monitoring, and secure clinical collaboration using the **Google Agent Development Kit (ADK)** and the **Agent-to-Agent (A2A) protocol**.

---

## 🚀 Key Features
- **Privacy-by-Design Ambient Monitoring**: Uses simulated camera-free micro-radar / RF sensors to track gait speed, sleep quality, and daily vitals without invasive video surveillance.
- **Proactive Empathy-Driven Companion**: Engages seniors in daily check-ins, orientation questions, and mild cognitive exercises using Gemini 2.5 Flash.
- **Clinical Medication Correlation**: Seamlessly queries openFDA and grounds drug interaction checks with Google Search to identify potential side effects of newly prescribed medications.
- **Cryptographic A2A Alert Routing**: Implements secure B2B/B2C handshakes to exchange health notifications with external Family and Physician agents.

---

## 📂 Project Structure
```
SilverGrove/
├── agents/              # Core ADK Agents
│   ├── sensory_guardian.py
│   ├── cognitive_companion.py
│   ├── medical_compliance.py
│   └── care_coordinator.py
├── mcp_servers/         # Model Context Protocol Servers
│   ├── vitals_server.py
│   └── medical_devices_server.py
├── tools/               # Agent Tools & Functions
│   ├── vitals_tools.py
│   ├── medication_tools.py
│   └── alert_tools.py
├── data/                # Mock telemetry & patient profiles
│   ├── residents.json
│   └── drug_interactions.json
├── frontend/            # High-Fidelity Glassmorphic Dashboard
│   ├── index.html
│   ├── style.css
│   └── script.js
├── a2a/                 # A2A endpoints & mock clients
│   ├── agent_card.json
│   ├── family_client.py
│   └── physician_client.py
├── .github/             # CI/CD Workflows
│   └── workflows/
│       └── deploy.yml
├── .gitignore
├── agent.py             # Root ADK Orchestrator
├── main.py              # FastAPI server + A2A routes
├── Dockerfile
└── requirements.txt
```
