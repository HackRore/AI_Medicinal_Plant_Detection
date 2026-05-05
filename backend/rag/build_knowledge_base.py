import os
import asyncio
import chromadb
from chromadb.config import Settings
import sys

# Add parent dir to path to import app services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.gemini_service import gemini_service
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()

    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
    return chunks

async def build_kb():
    print("Initializing ChromaDB...")
    persist_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
    client = chromadb.PersistentClient(path=persist_directory)
    
    collection_name = "plantoai_botanical_knowledge"
    # Delete if exists to rebuild
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    collection = client.create_collection(name=collection_name)
    
    monograph_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "monographs")
    if not os.path.exists(monograph_dir):
        print(f"Error: {monograph_dir} not found.")
        return

    files = [f for f in os.listdir(monograph_dir) if f.endswith(".txt")]
    print(f"Found {len(files)} monographs. Chunking and embedding...")
    
    all_chunks = []
    all_metadatas = []
    all_ids = []
    
    for filename in files:
        plant_name = filename.replace(".txt", "").replace("_", " ").title()
        with open(os.path.join(monograph_dir, filename), "r", encoding="utf-8") as f:
            content = f.read()
            chunks = chunk_text(content)
            for i, chunk in enumerate(chunks):
                chunk_id = f"{filename}_{i}"
                all_chunks.append(chunk)
                all_metadatas.append({"source": filename, "plant": plant_name})
                all_ids.append(chunk_id)

    print(f"Total chunks: {len(all_chunks)}. Generating embeddings...")
    
    # Process in batches to avoid rate limits
    batch_size = 5
    for i in range(0, len(all_chunks), batch_size):
        batch_chunks = all_chunks[i:i + batch_size]
        batch_ids = all_ids[i:i + batch_size]
        batch_metadatas = all_metadatas[i:i + batch_size]
        
        embeddings = []
        for chunk in batch_chunks:
            emb = await gemini_service.embed_text(chunk)
            if not emb:
                # Fallback to zero vector if embedding fails (should not happen in production)
                emb = [0.0] * 768 
            embeddings.append(emb)
        
        collection.add(
            embeddings=embeddings,
            documents=batch_chunks,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        print(f"Indexed batch {i//batch_size + 1}/{(len(all_chunks)-1)//batch_size + 1}")

    print(f"Knowledge base built. {len(all_chunks)} chunks indexed.")

if __name__ == "__main__":
    asyncio.run(build_kb())
