from __future__ import annotations

import chromadb
from chromadb.config import Settings
from ..config import config

_client = None
_collection = None


def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=config.chroma_path,
            settings=Settings(anonymized_telemetry=False),
        )
        _collection = _client.get_or_create_collection(
            name="vaultmind",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def upsert(chunk_id: str, embedding: list[float], metadata: dict, document: str):
    get_collection().upsert(
        ids=[chunk_id],
        embeddings=[embedding],
        metadatas=[metadata],
        documents=[document],
    )


def upsert_batch(ids: list[str], embeddings: list[list[float]], metadatas: list[dict], documents: list[str]):
    get_collection().upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents,
    )


def search(embedding: list[float], top_k: int) -> list[dict]:
    results = get_collection().query(
        query_embeddings=[embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    out = []
    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]
        score = 1.0 - distance  # cosine distance -> similarity
        out.append({
            "id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "score": round(score, 4),
        })
    return out


def delete_by_file(file_path: str):
    col = get_collection()
    existing = col.get(where={"file_path": {"$eq": file_path}})
    if existing["ids"]:
        col.delete(ids=existing["ids"])
