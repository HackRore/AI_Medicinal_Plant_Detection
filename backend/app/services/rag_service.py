class RagService:
    async def query_monographs(self, query: str) -> str:
        # Mock retrieval from Ayurvedic vector store
        return f"Ayurvedic context for {query}."

rag_service = RagService()
