import json
import urllib.request
import urllib.parse
from typing import Dict, Any

# Highly detailed mock drug interaction database for offline robustness
LOCAL_DRUG_DATABASE = {
    "metoprolol": {
        "generic_name": "Metoprolol Succinate",
        "brand_name": "Toprol-XL",
        "side_effects": [
            "Orthostatic hypotension (dizziness when standing up suddenly)",
            "Bradycardia (excessively slow heart rate)",
            "Fatigue and extreme tiredness",
            "Dizziness or lightheadedness",
            "Shortness of breath"
        ],
        "warnings": "Caution in elderly patients. Risk of orthostatic hypotension which can trigger severe falls. Do not abruptly stop taking this medication.",
        "interactions": {
            "lisinopril": "Co-administration of beta-blockers (Metoprolol) and ACE inhibitors (Lisinopril) can cause additive blood pressure lowering, increasing the risk of acute dizziness, hypotension, and falling."
        }
    },
    "lisinopril": {
        "generic_name": "Lisinopril",
        "brand_name": "Prinivil",
        "side_effects": [
            "Dry cough",
            "Dizziness / lightheadedness",
            "Hyperkalemia (high blood potassium levels)",
            "Headache"
        ],
        "warnings": "Monitor renal function and potassium levels. Stand up slowly to prevent orthostatic dizziness.",
        "interactions": {
            "metoprolol": "Increased hypotensive effect. Monitor blood pressure closely."
        }
    },
    "donepezil": {
        "generic_name": "Donepezil HCl",
        "brand_name": "Aricept",
        "side_effects": [
            "Nausea and vomiting",
            "Diarrhea",
            "Insomnia",
            "Muscle cramps"
        ],
        "warnings": "Can cause bradycardia and heart block. Monitor heart rate closely.",
        "interactions": {}
    }
}

def clean_drug_name(drug_name: str) -> str:
    """Normalize drug name by stripping dosage details or punctuation."""
    name = drug_name.lower().strip()
    # If the user passed something like "Metoprolol Succinate 50mg", isolate the first word
    words = name.split()
    if words:
        return words[0]
    return name

def check_drug_side_effects(drug_name: str) -> str:
    """
    Search the official US FDA openFDA database for a drug's adverse reactions and warnings.
    No API key required. High reliability, zero cost.
    """
    normalized = clean_drug_name(drug_name)
    encoded_name = urllib.parse.quote(f'openfda.brand_name:"{normalized}"+OR+openfda.generic_name:"{normalized}"')
    url = f'https://api.fda.gov/drug/label.json?search={encoded_name}&limit=1'
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            results = data.get("results", [])
            if results:
                result = results[0]
                
                # Extract adverse reactions, warnings, or precautions
                adverse_reactions = result.get("adverse_reactions", ["No detailed adverse reactions listed."])[0]
                warnings = result.get("warnings_and_cautions", result.get("warnings", ["No direct warnings section found."]))[0]
                
                # Truncate to prevent token blowouts, retaining rich medical context
                summary = (
                    f"### openFDA Drug Info: {drug_name.upper()}\n\n"
                    f"**Adverse Reactions / Side Effects (FDA):**\n"
                    f"{adverse_reactions[:800]}...\n\n"
                    f"**Warnings & Precautions (FDA):**\n"
                    f"{warnings[:800]}..."
                )
                return summary
    except Exception as e:
        # Fall back gracefully to our rich local drug database
        pass
        
    # Local fallback
    if normalized in LOCAL_DRUG_DATABASE:
        info = LOCAL_DRUG_DATABASE[normalized]
        return (
            f"### Local Clinical Info: {drug_name.upper()} (Fallback Enabled)\n\n"
            f"**Generic Name:** {info['generic_name']}\n"
            f"**Brand Name:** {info['brand_name']}\n\n"
            f"**Common Side Effects:**\n" + "\n".join([f"- {se}" for se in info['side_effects']]) + "\n\n"
            f"**Geriatric Warnings:**\n"
            f"{info['warnings']}"
        )
    
    return f"No openFDA label or local database record found for drug '{drug_name}'."

def check_drug_interactions(medications: list) -> str:
    """
    Cross-reference a list of drugs to check for dangerous drug-drug interactions.
    """
    clean_meds = [clean_drug_name(med) for med in medications]
    interactions_found = []
    
    for i, med1 in enumerate(clean_meds):
        for med2 in clean_meds[i+1:]:
            # Check med1 -> med2 local interactions
            if med1 in LOCAL_DRUG_DATABASE and med2 in LOCAL_DRUG_DATABASE[med1]["interactions"]:
                interactions_found.append(
                    f"⚠️ **DANGEROUS INTERACTION DETECTED** between **{medications[i]}** and **{medications[clean_meds.index(med2)]}**:\n"
                    f"{LOCAL_DRUG_DATABASE[med1]['interactions'][med2]}"
                )
            # Check med2 -> med1 local interactions
            elif med2 in LOCAL_DRUG_DATABASE and med1 in LOCAL_DRUG_DATABASE[med2]["interactions"]:
                interactions_found.append(
                    f"⚠️ **DANGEROUS INTERACTION DETECTED** between **{medications[clean_meds.index(med2)]}** and **{medications[i]}**:\n"
                    f"{LOCAL_DRUG_DATABASE[med2]['interactions'][med1]}"
                )
                
    if interactions_found:
        return "\n\n".join(interactions_found)
    return "No known dangerous interactions found between active medications."

if __name__ == "__main__":
    # Test openFDA lookup
    print(check_drug_side_effects("Metoprolol"))
    # Test interaction check
    print(check_drug_interactions(["Metoprolol", "Lisinopril"]))
