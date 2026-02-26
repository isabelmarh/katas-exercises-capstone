from dataclasses import dataclass
from typing import Any, Dict, Sequence

import chromadb


@dataclass(frozen=True)
class Hit:
    id: str
    score: float
    text: str
    metadata: Dict[str, Any]


class ChromaClient:
    def __init__(self):
        self.client = chromadb.Client()
        self.name = "meeting_transcripts"
        self._create()

    def _create(self):
        self.collection = self.client.get_or_create_collection(
            name=self.name, metadata={"hnsw:space": "cosine"}
        )

    def reset(self) -> None:
        try:
            self.client.delete_collection(name=self.name)
        except Exception:
            pass
        finally:
            self._create()

    def upsert_chunks(
        self,
        ids: Sequence[str],
        embeddings: Sequence[Sequence[float]],
        documents: Sequence[str],
        metadatas: Sequence[dict[str, Any]],
    ) -> None:
        self.collection.upsert(
            ids=ids,  # pyright: ignore[reportArgumentType]
            embeddings=embeddings,  # pyright: ignore[reportArgumentType]
            documents=documents,  # pyright: ignore[reportArgumentType]
            metadatas=metadatas,  # pyright: ignore[reportArgumentType]
        )

    def query(self, embedding: Sequence[float], n_results: int = 5):
        res = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["documents", "distances", "metadatas"],
        )

        ids = res["ids"][0]
        assert res["documents"]
        docs = res["documents"][0]
        assert res["distances"]
        dists = res["distances"][0]
        assert res["metadatas"]
        metas = res["metadatas"][0]

        hits: list[Hit] = []
        for _id, doc, dist, meta in zip(ids, docs, dists, metas):
            hits.append(
                Hit(
                    id=_id,
                    score=1.0 - float(dist),  # cosine distance -> similarity
                    text=doc,
                    metadata=meta or {},  # pyright: ignore[reportArgumentType]
                )
            )
        return hits
