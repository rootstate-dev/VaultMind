import json
import logging
import threading
from mcp.server.fastmcp import FastMCP
from vaultmind.config import config
from vaultmind.infrastructure.embedder import embed
from vaultmind.infrastructure.store import search
from vaultmind.infrastructure.repository import get_all_paths, get_content, write_note
from vaultmind.services.indexer import index_all, index_file
from vaultmind.infrastructure.watcher import start_watcher

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

mcp = FastMCP("vaultmind")


@mcp.tool()
def knowledge_search(query: str, top_k: int = 0) -> str:
    """Performs semantic search in the Obsidian vault. Returns the most relevant note sections for a given query."""
    k = top_k if top_k > 0 else config.top_k
    embedding = embed(query)
    results = search(embedding, k)
    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
def knowledge_get(file_path: str) -> str:
    """Retrieves the full content of a specific note by its relative path."""
    content = get_content(file_path)
    return content if content is not None else f"File not found: {file_path}"


@mcp.tool()
def knowledge_write(title: str, content: str, tags: list[str] | None = None) -> str:
    """Writes a new note to the Obsidian vault and indexes it immediately."""
    relative_path = write_note(title, content, tags or [])
    index_file(relative_path)
    return f"Note written and indexed: {relative_path}"


@mcp.tool()
def knowledge_sync() -> str:
    """Re-indexes all notes in the vault."""
    count = index_all()
    return f"Sync complete. Indexed {count} files."


def _startup():
    logger.info("Starting background indexing of %s", config.vault_path)
    index_all()
    start_watcher()
    logger.info("Indexing complete and watcher started.")


def main():
    import os
    if not os.path.isdir(config.vault_path):
        raise ValueError(f"VAULT_PATH does not exist: {config.vault_path}")
    threading.Thread(target=_startup, daemon=True).start()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
