// SilverGrove Client Side Orchestrator
let activeResidentId = null;

function getApiBaseUrl() {
    return localStorage.getItem("silvergrove_api_url") || "";
}

document.addEventListener("DOMContentLoaded", () => {
    initResidents();
    initAlerts();

    // Event listeners
    document.getElementById("trigger-check-btn").addEventListener("click", triggerAgentCheck);
    document.getElementById("clear-btn").addEventListener("click", clearAlertTimeline);
    document.getElementById("modal-ack-btn").addEventListener("click", closeModal);
    
    // Backend config listeners
    document.getElementById("config-backend-btn").addEventListener("click", openConfigModal);
    document.getElementById("config-close-btn").addEventListener("click", closeConfigModal);
    document.getElementById("config-reset-btn").addEventListener("click", resetConfigToLocal);
    document.getElementById("config-connect-btn").addEventListener("click", connectToBackend);
});

function openConfigModal() {
    const input = document.getElementById("input-backend-url");
    input.value = getApiBaseUrl();
    document.getElementById("config-status").innerText = "";
    document.getElementById("modal-config").classList.remove("hidden");
}

function closeConfigModal() {
    document.getElementById("modal-config").classList.add("hidden");
}

function resetConfigToLocal() {
    localStorage.removeItem("silvergrove_api_url");
    document.getElementById("config-status").style.color = "var(--color-success)";
    document.getElementById("config-status").innerText = "Switched to Localhost backend!";
    setTimeout(() => {
        closeConfigModal();
        window.location.reload();
    }, 1000);
}

async function connectToBackend() {
    let url = document.getElementById("input-backend-url").value.trim();
    if (!url) {
        document.getElementById("config-status").style.color = "var(--color-danger)";
        document.getElementById("config-status").innerText = "URL cannot be empty.";
        return;
    }
    
    // Standardize URL formatting
    if (url.endsWith("/")) {
        url = url.slice(0, -1);
    }
    
    document.getElementById("config-status").style.color = "var(--color-info)";
    document.getElementById("config-status").innerText = "Validating connection...";
    
    try {
        const res = await fetch(url + "/api/residents");
        if (res.ok) {
            localStorage.setItem("silvergrove_api_url", url);
            document.getElementById("config-status").style.color = "var(--color-success)";
            document.getElementById("config-status").innerText = "Connected successfully!";
            setTimeout(() => {
                closeConfigModal();
                window.location.reload();
            }, 1000);
        } else {
            throw new Error("Endpoint returned status " + res.status);
        }
    } catch (err) {
        document.getElementById("config-status").style.color = "var(--color-danger)";
        document.getElementById("config-status").innerText = "Failed to connect. Ensure URL is correct and CORS is enabled.";
        console.error(err);
    }
}

// Load the Resident list into sidebar
async function initResidents() {
    try {
        const res = await fetch(getApiBaseUrl() + "/api/residents");
        const residents = await res.json();
        
        const listContainer = document.getElementById("residents-list");
        listContainer.innerHTML = "";
        
        if (residents.length === 0) {
            listContainer.innerHTML = "<p class='placeholder-text'>No residents configured.</p>";
            return;
        }

        residents.forEach((r, idx) => {
            const card = document.createElement("div");
            card.className = `resident-card glass-panel-inner ${idx === 0 ? "active" : ""}`;
            card.dataset.id = r.id;
            
            card.innerHTML = `
                <div class="res-header">
                    <span class="res-name">${r.name}</span>
                    <span class="res-age">Age ${r.age}</span>
                </div>
                <div class="res-meta">${r.conditions.slice(0, 2).join(", ")}</div>
            `;
            
            card.addEventListener("click", () => selectResident(r.id));
            listContainer.appendChild(card);
        });

        // Select the first resident by default
        if (residents.length > 0) {
            selectResident(residents[0].id);
        }

    } catch (e) {
        console.error("Error loading residents:", e);
        document.getElementById("residents-list").innerHTML = "<p class='status-pill status-failed'>Failed to connect to backend.</p>";
    }
}

// Handle switching residents
async function selectResident(residentId) {
    activeResidentId = residentId;
    
    // Manage UI active card classes
    document.querySelectorAll(".resident-card").forEach(card => {
        if (card.dataset.id === residentId) {
            card.classList.add("active");
        } else {
            card.classList.remove("active");
        }
    });

    // Reset workspace and agent cards
    resetAgentWorkspace();

    try {
        const res = await fetch(getApiBaseUrl() + `/api/residents/${residentId}`);
        const data = await res.json();
        
        const p = data.profile;
        const v = data.vitals;

        // Render Resident Profile Sidebar
        document.getElementById("selected-resident-profile").classList.remove("hidden");
        document.getElementById("prof-name").innerText = p.name;
        document.getElementById("prof-age").innerText = p.age;
        document.getElementById("prof-cond").innerText = p.conditions.join(", ");
        
        const medsList = document.getElementById("prof-meds-list");
        medsList.innerHTML = "";
        p.medications.forEach(m => {
            const li = document.createElement("li");
            li.innerHTML = `<strong>${m.name}</strong> (${m.dose})<br><span style='color: var(--color-text-muted)'>${m.frequency}</span>`;
            medsList.appendChild(li);
        });

        // Render Ambient Sensor Telemetry
        document.getElementById("vital-hr").innerText = v.telemetry.heart_rate_bpm;
        document.getElementById("base-hr").innerText = v.baselines.heart_rate_bpm;
        
        document.getElementById("vital-bp").innerText = `${v.telemetry.bp_systolic}/${v.telemetry.bp_diastolic}`;
        document.getElementById("bp-deviation").innerText = `Baseline: ${v.baselines.bp_systolic}/${v.baselines.bp_diastolic}`;
        
        document.getElementById("vital-gait").innerText = v.telemetry.gait_speed_ms;
        document.getElementById("gait-deviation").innerText = `Baseline: ${v.baselines.gait_speed_ms} m/s`;
        
        document.getElementById("vital-sleep").innerText = v.telemetry.sleep_hours;
        document.getElementById("base-sleep").innerText = v.baselines.sleep_hours;
        
        document.getElementById("vital-occupancy").innerText = v.telemetry.room_occupancy.replace('_', ' ').toUpperCase();

        // Highlight Telemetry Anomalies
        const bpCard = document.getElementById("card-bp");
        const gaitCard = document.getElementById("card-gait");
        
        bpCard.classList.remove("anomaly-alert");
        gaitCard.classList.remove("anomaly-alert");
        
        if (v.status === "ANOMALY_DETECTED") {
            if (v.telemetry.bp_systolic >= 140 || v.telemetry.bp_systolic <= 100) {
                bpCard.classList.add("anomaly-alert");
            }
            if (v.gait_change_percent <= -15.0) {
                gaitCard.classList.add("anomaly-alert");
            }
        }

    } catch (e) {
        console.error("Error fetching resident details:", e);
    }
}

// Reset Agent workspace back to empty/waiting state
function resetAgentWorkspace() {
    const agents = ["sensory", "compliance", "companion", "coordinator"];
    agents.forEach(a => {
        const col = document.getElementById(`agent-${a}`);
        col.querySelector(".status-pill").className = "status-pill status-waiting";
        col.querySelector(".status-pill").innerText = "Waiting";
        
        const box = col.querySelector(".agent-output-box");
        if (a === "sensory") box.innerHTML = "<p class='placeholder-text'>Waiting to ingest vital telemetry streams...</p>";
        if (a === "compliance") box.innerHTML = "<p class='placeholder-text'>Waiting for sensory anomaly escalation...</p>";
        if (a === "companion") box.innerHTML = "<p class='placeholder-text'>Waiting for clinical findings check-in draft...</p>";
        if (a === "coordinator") box.innerHTML = "<p class='placeholder-text'>Waiting to dispatch A2A cryptographic alerts...</p>";
    });
}

// Staggered Visual Agent Progress Simulation helper
function setAgentStatus(agentKey, statusText, statusClass) {
    const col = document.getElementById(`agent-${agentKey}`);
    const pill = col.querySelector(".status-pill");
    pill.className = `status-pill ${statusClass}`;
    pill.innerText = statusText;
}

// Trigger Multi-Agent Orchestrator health checkup
async function triggerAgentCheck() {
    if (!activeResidentId) return;

    const btn = document.getElementById("trigger-check-btn");
    btn.disabled = true;
    btn.innerText = "Analyzing Telemetry...";

    // Reset workspace before check
    resetAgentWorkspace();

    // Start Staggered Agent Telemetry Track Animation
    setAgentStatus("sensory", "Analyzing Vitals", "status-running");
    
    try {
        const response = await fetch(getApiBaseUrl() + `/api/residents/${activeResidentId}/check`, {
            method: "POST"
        });
        const trajectory = await response.json();
        
        // 1. Sensory Guardian completes
        setAgentStatus("sensory", "Completed", "status-completed");
        const sensoryBox = document.getElementById("agent-sensory").querySelector(".agent-output-box");
        sensoryBox.innerHTML = `<div style='animation: fadeIn 0.4s ease'>${formatMarkdown(trajectory.sensory_guardian.output)}</div>`;
        
        // Check if escalation occurred
        if (trajectory.medical_compliance.status === "SKIPPED") {
            setAgentStatus("compliance", "Skipped", "status-waiting");
            setAgentStatus("companion", "Skipped", "status-waiting");
            setAgentStatus("coordinator", "Skipped", "status-waiting");
            btn.disabled = false;
            btn.innerText = "Run Multi-Agent Health Check";
            return;
        }

        // 2. Compliance active
        setAgentStatus("compliance", "Running FDA Lookups", "status-running");
        await delay(1200);
        setAgentStatus("compliance", "Completed", "status-completed");
        const compBox = document.getElementById("agent-compliance").querySelector(".agent-output-box");
        compBox.innerHTML = `<div style='animation: fadeIn 0.4s ease'>${formatMarkdown(trajectory.medical_compliance.output)}</div>`;

        // 3. Companion active
        setAgentStatus("companion", "Composing Empathy Dialog", "status-running");
        await delay(1200);
        setAgentStatus("companion", "Completed", "status-completed");
        const compaBox = document.getElementById("agent-companion").querySelector(".agent-output-box");
        compaBox.innerHTML = `<div style='animation: fadeIn 0.4s ease'><strong>Empathetic Dialogue:</strong><br><br><em>"${trajectory.cognitive_companion.output}"</em></div>`;

        // 4. Coordinator active
        setAgentStatus("coordinator", "Routing Outbound A2A", "status-running");
        await delay(1200);
        setAgentStatus("coordinator", "Completed", "status-completed");
        const coordBox = document.getElementById("agent-coordinator").querySelector(".agent-output-box");
        coordBox.innerHTML = `<div style='animation: fadeIn 0.4s ease'>${formatMarkdown(trajectory.care_coordinator.output)}</div>`;

        // Refresh the outbound timeline feed
        initAlerts();

        // Trigger premium overlay warning modal if warning/critical
        triggerModalAlert(trajectory);

    } catch (e) {
        console.error("Agent execution failed:", e);
        setAgentStatus("sensory", "Failed", "status-failed");
    } finally {
        btn.disabled = false;
        btn.innerText = "Run Multi-Agent Health Check";
    }
}

// Modal popup launcher for alerts
function triggerModalAlert(trajectory) {
    const modal = document.getElementById("modal-alert");
    
    // Parse findings from the correlation report to present inside modal
    const complianceText = trajectory.medical_compliance.output;
    const companionText = trajectory.cognitive_companion.output;
    
    document.getElementById("modal-message").innerHTML = `
        <strong>Observed Anomaly:</strong> Ambient camera-free telemetry detected critical gait speed velocity slowdown and blood pressure shifts for the resident.<br><br>
        <strong>Empathy Guidance:</strong> "${companionText}"
    `;
    
    // Extract interaction notes dynamically
    let interaction = "Hypotensive risks associated with medication introduction. Advise standing slowly, hydration, and observation.";
    if (complianceText.includes("lisinopril") || complianceText.includes("Lisinopril")) {
        interaction = "Dangerous drug-drug interactions between Metoprolol and Lisinopril. High risk of orthostatic hypotension and fall accidents.";
    } else if (complianceText.includes("Sinemet") || complianceText.includes("Levodopa")) {
        interaction = "Parkinsonian motor fluctuations and freezing of gait triggered by Sinemet (Carbidopa-Levodopa) dosage introduction. High fall risk.";
    } else if (complianceText.includes("Oxycodone")) {
        interaction = "CNS depression and postural instability triggered by post-op Oxycodone opioid administration. High somnolence and fall risk.";
    }
    document.getElementById("modal-correlation").innerText = interaction;
    
    // Format actions list - strictly no emojis!
    const actionList = document.getElementById("modal-actions-list");
    actionList.innerHTML = `
        <li>[!] Guide resident to hydrate immediately and stand up slowly</li>
        <li>[!] Notify family representative agent over active A2A node</li>
        <li>[!] Request primary care physician review pharmacological dosages</li>
    `;

    modal.classList.remove("hidden");
}

function closeModal() {
    document.getElementById("modal-alert").classList.add("hidden");
}

// Fetch active outbound A2A alerts from timeline
async function initAlerts() {
    try {
        const res = await fetch(getApiBaseUrl() + "/api/alerts");
        const alerts = await res.json();
        
        const timeline = document.getElementById("alerts-timeline");
        timeline.innerHTML = "";
        
        if (alerts.length === 0) {
            timeline.innerHTML = `
                <div class="no-alerts-placeholder">
                    <span class="timeline-empty-icon" style="display: flex; align-items: center; justify-content: center; color: #475569; margin-bottom: 0.8rem;">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                            <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                        </svg>
                    </span>
                    <p>No active alerts dispatched. System running in baseline safety thresholds.</p>
                </div>
            `;
            return;
        }

        alerts.forEach(alert => {
            const item = document.createElement("div");
            const severityClass = alert.severity === "CRITICAL" ? "critical" : "warning";
            item.className = `alert-feed-item glass-panel-inner ${severityClass}`;
            
            const date = new Date(alert.timestamp);
            const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            item.innerHTML = `
                <div class="alert-item-header">
                    <span class="alert-item-title">${alert.resident_name} (${alert.severity})</span>
                    <span class="alert-item-time">${timeStr}</span>
                </div>
                <div class="alert-item-msg">${alert.message}</div>
                ${alert.correlation ? `<div class="alert-item-msg" style="color: #fda4af; font-size: 11px; margin-top: 4px;">[x] Correlation: ${alert.correlation.slice(0, 120)}...</div>` : ''}
                <div class="alert-item-tag">A2A DISPATCHED • SIGNED</div>
            `;
            timeline.appendChild(item);
        });

    } catch (e) {
        console.error("Error loading alert timeline:", e);
    }
}

// Clear alerts timeline
async function clearAlertTimeline() {
    if (!confirm("Are you sure you want to clear the A2A alert log history?")) return;
    try {
        await fetch(getApiBaseUrl() + "/api/alerts/clear", { method: "POST" });
        initAlerts();
    } catch (e) {
        console.error(e);
    }
}

// Helper: Basic Markdown to HTML converter for agent responses
function formatMarkdown(text) {
    if (!text) return "";
    return text
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>")
        .replace(/### (.*?)(<br>|$)/g, "<h4 style='font-family: Outfit, sans-serif; font-size: 14px; margin: 10px 0 6px; color: white;'>$1</h4>")
        .replace(/## (.*?)(<br>|$)/g, "<h3 style='font-family: Outfit, sans-serif; font-size: 16px; margin: 14px 0 8px; color: white;'>$1</h3>");
}

// Helper: Delay utility for animations
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
