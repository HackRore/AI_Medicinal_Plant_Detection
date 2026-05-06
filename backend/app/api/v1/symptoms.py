from fastapi import APIRouter, HTTPException, Request
from app.services.rag_service import rag_service
from app.services.gemini_service import gemini_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("")
async def search_symptoms(request: Request):
    """Executes RAG-powered botanical diagnostics based on user symptoms."""
    try:
        diagnostic_request = await request.json()
        symptoms_text = diagnostic_request.get("symptoms", "").strip()
        
        if not symptoms_text:
            raise HTTPException(status_code=400, detail="Symptom description required")

        # Contextual retrieval from Ayurvedic vector store
        vector_context = await rag_service.query_monographs(symptoms_text)
        
        # Grounded reasoning via Gemini
        clinical_insight = await gemini_service.get_rag_symptom_analysis(
            symptoms_text, 
            vector_context
        )

        return {
            "success": True,
            "analysis": clinical_insight,
            "retrieval_meta": {
                "context_length": len(vector_context),
                "engine": "chroma_v1_mpnet"
            }
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Symptom diagnostic pipeline failed: {str(e)}")
        return {
            "success": False, 
            "error": "DIAGNOSTIC_FAILURE",
            "detail": "Vector retrieval or reasoning engine timed out"
        }
