import re
import json
import logging

logger = logging.getLogger(__name__)

def safe_parse_gemini_json(text: str) -> dict:
    """
    Robustly extracts and parses JSON from Gemini responses.
    Handles markdown backticks, extra text, and malformed structures.
    """
    if not text:
        return {}
    
    # Remove markdown backticks if present
    cleaned = re.sub(r'```(?:json)?\s*|\s*```', '', text).strip()
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try finding JSON block with regex
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse regex-extracted JSON: {match.group()[:100]}")
    
    return {}
