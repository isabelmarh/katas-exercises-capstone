from dataclasses import dataclass
from typing import Any, Dict

import chromadb

@dataclass(frozen=True)
class Hit:
    id: str
    score: float
    metadata: Dict[str, Any]

class ChromaClient:
    def __init__(self):
        self.client = chromadb.Client()
        self.name = "meeting_transcripts"
        
    def _create(self) -> None:
        self.collection = self.client.get_or_create_collection(
            name=self.name,
            metadata={"hnsw:space": "cosine"}
        )

    def reset(self) -> None:
        try:
            self.client.delete_collection(name=self.name)
        except Exception:
            pass
        finally:
            self._create()


    def upsert_chunks(self, ids: list[str], embeddings: list[list[float]], documents: list[str], metadatas: list[dict]):
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(self, embedding: list[float], n_results: int = 5):
        res = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["documents", "distances", "metadatas"],
        )

        ids = res["ids"][0]
        docs = res["documents"][0]
        dists = res["distances"][0]
        metas = res["metadatas"][0]

        hits = []
        for _id, doc, dist, meta in zip(ids, docs, dists, metas):
            hits.append({
                "id": _id,
                "score": 1.0 - float(dist),  # cosine distance -> similarity
                "text": doc,
                "metadata": meta or {},
            })
        return hits