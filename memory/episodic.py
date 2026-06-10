"""Episodic memory backed by a local ChromaDB vector store."""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

_EMBED_MODEL = "all-MiniLM-L6-v2"
_COLLECTION_NAME = "episodic_memory"
_PERSIST_DIR = "chroma_store"


class EpisodicMemory:
    """Persists past session messages in ChromaDB and retrieves them by semantic similarity."""

    def __init__(self):
        self._client = chromadb.PersistentClient(
            path=_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(_COLLECTION_NAME)
        self._embedder = SentenceTransformer(_EMBED_MODEL)

    def save_session(self, session_id: int, messages: list[dict]) -> None:
        """Embed and store all messages from a completed session."""
        for idx, msg in enumerate(messages):
            doc_id = f"s{session_id}_m{idx}"
            self._collection.upsert(
                ids=[doc_id],
                documents=[msg["content"]],
                embeddings=[self._embedder.encode(msg["content"]).tolist()],
                metadatas=[{
                    "session_id": session_id,
                    "turn_index": idx,
                    "role": msg["role"],
                }],
            )

    def search(self, query: str, top_k: int = 3) -> list[str]:
        """Return the top_k most semantically relevant past messages for *query*."""
        if self._collection.count() == 0:
            return []
        query_embedding = self._embedder.encode(query).tolist()
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self._collection.count()),
        )
        return results["documents"][0] if results["documents"] else []
