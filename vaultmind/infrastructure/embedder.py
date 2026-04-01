from sentence_transformers import SentenceTransformer
from ..config import config

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(config.embedding_model)
    return _model


def embed(text: str) -> list[float]:
    return get_model().encode(text, normalize_embeddings=True).tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    return get_model().encode(texts, normalize_embeddings=True, batch_size=32).tolist()
