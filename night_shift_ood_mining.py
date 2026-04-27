import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- SPRINT 1 PHASE B: OOD Dataset Setup ---

# 1. Update class_names.json to include the 82nd class
CLASS_FILE = os.path.join("backend", "app", "data", "class_names.json")

try:
    if os.path.exists(CLASS_FILE):
        with open(CLASS_FILE, "r") as f:
            classes = json.load(f)
        
        # Check if OOD class already exists
        ood_exists = any("Unknown" in c.get("name", "") for c in classes if isinstance(c, dict))
        if not ood_exists:
            classes.append({
                "name": "Unknown / Not in Database",
                "scientific_name": "Out of Distribution",
                "warning": "This is a non-medicinal plant or an out-of-focus image."
            })
            with open(CLASS_FILE, "w") as f:
                json.dump(classes, f, indent=4)
            logger.info("Added 'Unknown / Not in Database' as the 82nd class.")
        else:
            logger.info("OOD class already exists in registry.")
except Exception as e:
    logger.error(f"Failed to update class_names.json: {e}")

# 2. Update KB
KB_FILE = os.path.join("backend", "app", "data", "medicinal_knowledge_v2.json")
try:
    if os.path.exists(KB_FILE):
        with open(KB_FILE, "r") as f:
            kb = json.load(f)
        
        if not any(entry.get("scientific_name") == "N/A" for entry in kb):
            kb.append({
                "scientific_name": "N/A",
                "common_names": ["Unknown", "Weed", "Non-Medicinal", "Unknown / Not in Database"],
                "family": "N/A",
                "native_region": "Global",
                "toxicity": {"level": "high", "level_code": 1, "notes": "Do not consume unidentified plants."},
                "description": "This plant does not strongly match any of our verified medicinal species. It may be a weed, a non-medicinal plant, or an out-of-focus image.",
                "medicinal_properties": [],
                "ayurvedic_uses": [],
                "preparation": "DO NOT PREPARE.",
                "active_compounds": [],
                "contraindications": ["Do not ingest."]
            })
            with open(KB_FILE, "w") as f:
                json.dump(kb, f, indent=4)
            logger.info("Added OOD profile to Ayurvedic Knowledge Base.")
        else:
            logger.info("OOD profile already exists in KB.")
except Exception as e:
    logger.error(f"Failed to update KB: {e}")

logger.info("Night Shift Task: OOD Hard Negative Class Registration COMPLETE.")
