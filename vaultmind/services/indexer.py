import logging
from pathlib import Path
from ..infrastructure.chunker import chunk_file
from ..infrastructure.embedder import embed_batch
from ..infrastructure.store import upsert_batch, delete_by_file
from ..infrastructure.repository import get_all_paths
from ..config import config

logger = logging.getLogger(__name__)


def index_file(relative_path: str):
    full_path = Path(config.vault_path) / relative_path
    if not full_path.exists():
        logger.warning("File not found: %s", relative_path)
        return

    try:
        delete_by_file(relative_path)
        chunks = chunk_file(str(full_path), relative_path)

        if not chunks:
            return

        texts = [c.content for c in chunks]
        embeddings = embed_batch(texts)

        upsert_batch(
            ids=[c.id for c in chunks],
            embeddings=embeddings,
            metadatas=[{"file_path": c.file_path, "heading": c.heading, "chunk_index": c.chunk_index} for c in chunks],
            documents=texts,
        )
        logger.info("Indexed %d chunks for %s", len(chunks), relative_path)
    except Exception:
        logger.exception("Failed to index %s", relative_path)


def index_all() -> int:
    paths = get_all_paths()
    for path in paths:
        index_file(path)
    return len(paths)
