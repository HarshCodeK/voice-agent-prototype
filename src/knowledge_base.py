import os
import glob
import chromadb
from sentence_transformers import SentenceTransformer

FAQ_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "faq_docs")
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
COLLECTION_NAME = "faq"

_model = None
_client = None
_collection = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = _client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection

def _chunk_text(text: str, chunk_size: int = 300) -> list[str]:
    words = text.split()
    chunks = []
    current = []
    current_len = 0
    for word in words:
        current.append(word)
        current_len += len(word) + 1
        if current_len >= chunk_size and word.endswith(('.', '!', '?')):
            chunks.append(" ".join(current))
            current = []
            current_len = 0
    if current:
        chunks.append(" ".join(current))
    return chunks

def build_knowledge_base():
    model = _get_model()
    collection = _get_collection()
    all_chunks = []
    ids = []
    metadatas = []
    idx = 0
    for filepath in glob.glob(os.path.join(FAQ_DIR, "*.txt")):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = _chunk_text(text)
        for chunk in chunks:
            all_chunks.append(chunk)
            ids.append(f"chunk_{idx}")
            metadatas.append({"source": os.path.basename(filepath)})
            idx += 1
    embeddings = model.encode(all_chunks).tolist()
    existing_ids = collection.get()["ids"]
    if existing_ids:
        collection.delete(ids=existing_ids)
    collection.add(ids=ids, embeddings=embeddings, documents=all_chunks, metadatas=metadatas)
    print(f"Stored {len(all_chunks)} chunks in ChromaDB collection '{COLLECTION_NAME}'")

def retrieve_faq_context(query: str, k: int = 3) -> list[str]:
    model = _get_model()
    collection = _get_collection()
    query_emb = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_emb, n_results=k)
    return results["documents"][0] if results["documents"] else []
