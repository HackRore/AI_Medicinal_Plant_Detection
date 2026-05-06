class RagService:
    def __init__(self):
        # Lazy initialization of ChromaDB
        self.collection = None

    def _init_chroma(self):
        if self.collection is None:
            # Mock ChromaDB initialization
            self.collection = "initialized"

    async def query_monographs(self, query: str) -> str:
        self._init_chroma()
        return f"Ayurvedic context for {query}."

_rag = None
def get_rag_service():
    global _rag
    if _rag is None:
        _rag = RagService()
    return _rag

# Expose rag_service for backwards compatibility, but it's lazy internally
rag_service = RagService()
