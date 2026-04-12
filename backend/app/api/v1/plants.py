from fastapi import APIRouter
from app.services.ml_service import ml_service

router = APIRouter()

@router.get("")
def list_plants(search: str = "", page: int = 1, limit: int = 20):
    """
    Modular plants repository sync.
    Syncs live with G9 knowledge base.
    """
    plants = []
    for key, val in ml_service.kb.items():
        entry = {
            "id": key.lower().replace(" ", "-"),
            "scientific_name": key,
            "common_names": val.get("common_names", []),
            "ayurvedic_uses": val.get("ayurvedic_uses", []),
            "toxicity": val.get("toxicity", {}),
            "family": val.get("family", ""),
            "description": val.get("description", ""),
            "native_region": val.get("native_region", "India")
        }
        
        if search:
            search_text = " ".join([key] + val.get("common_names", []) + [val.get("family", "")]).lower()
            if search.lower() not in search_text:
                continue
        plants.append(entry)
    
    total = len(plants)
    start = (page - 1) * limit
    end = start + limit
    
    return {
        "plants": plants[start:end],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@router.get("/{name}")
def get_plant(name: str):
    key = name.replace("-", " ")
    # Deep search in KB
    result = ml_service._kb(key)
    if not result:
        return {"error": "Botanical entry not found"}
    return {"scientific_name": key, **result}
