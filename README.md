# VaultMind

[![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/rootstate-dev/VaultMind?style=social)](https://github.com/rootstate-dev/VaultMind)
[![MCP](https://img.shields.io/badge/MCP-compatible-blueviolet)](https://modelcontextprotocol.io)
[![Powered by sentence-transformers](https://img.shields.io/badge/embeddings-sentence--transformers-orange)](https://www.sbert.net/)
[![ChromaDB](https://img.shields.io/badge/vector--db-ChromaDB-red)](https://www.trychroma.com/)
[![uv](https://img.shields.io/badge/package--manager-uv-black)](https://docs.astral.sh/uv/)

A local, privacy-first MCP (Model Context Protocol) server that connects your [Obsidian](https://obsidian.md) vault to any MCP-compatible AI assistant (Claude, Cursor, etc.) via semantic search. Ask questions and the AI retrieves the most relevant note sections from your vault automatically — **no API keys, no cloud, fully offline.**

## How it works

1. On startup, all `.md` files in your vault are chunked by heading and size
2. Each chunk is embedded using `all-MiniLM-L6-v2` (runs fully locally via sentence-transformers)
3. Embeddings are stored in a local ChromaDB vector database
4. Claude searches your vault semantically, retrieves full note content, writes new notes, and syncs changes
5. A file watcher automatically re-indexes notes when you edit them in Obsidian

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

## Setup

### 1. Install dependencies

```bash
cd VaultMind
uv sync
```

### 2. Configure your vault path

Edit `.env`:

```env
VAULT_PATH=C:/Users/yourname/path/to/your/obsidian/vault
```

### 3. Configure Claude Desktop

Open `%APPDATA%\Claude\claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "vaultmind": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\yourname\\OneDrive\\Desktop\\VaultMind-py",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```

Replace the `--directory` value with the actual path to this project.

### 4. Restart Claude Desktop

On first launch, `all-MiniLM-L6-v2` (~80MB) is downloaded from HuggingFace automatically. Background indexing starts immediately — wait ~1-2 minutes before searching.

## Configuration

All options are set in `.env`:

| Variable | Default | Description |
|---|---|---|
| `VAULT_PATH` | *(required)* | Absolute path to your Obsidian vault |
| `CHROMA_PATH` | `chroma_db` | Where ChromaDB stores its data |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence-transformers model name |
| `TOP_K` | `5` | Number of results returned per search |
| `MAX_CHUNK_CHARS` | `1600` | Maximum characters per chunk (~400 tokens) |
| `CHUNK_OVERLAP_CHARS` | `200` | Overlap between consecutive chunks |

## MCP Tools

| Tool | Description |
|---|---|
| `knowledge_search(query, top_k?)` | Semantic search across all notes |
| `knowledge_get(file_path)` | Get the full content of a note |
| `knowledge_write(title, content, tags?)` | Write a new note and index it immediately |
| `knowledge_sync()` | Re-index all notes (use after bulk external changes) |

## Re-indexing

The file watcher handles individual changes automatically. For a full rebuild:

1. Delete the `chroma_db/` directory
2. Restart Claude Desktop

## Project structure

```
VaultMind-py/
├── main.py                        # MCP server entry point and tool definitions
├── vaultmind/
│   ├── config.py                  # Configuration loaded from .env
│   ├── core/
│   │   └── models.py              # Chunk and SearchResult dataclasses
│   ├── infrastructure/
│   │   ├── chunker.py             # Splits markdown by heading and size
│   │   ├── embedder.py            # sentence-transformers wrapper
│   │   ├── store.py               # ChromaDB read/write operations
│   │   ├── repository.py          # Vault file I/O and note writing
│   │   └── watcher.py             # File system monitor for live re-indexing
│   └── services/
│       └── indexer.py             # Orchestrates chunking, embedding, and storing
├── .env                           # Your local config (not committed)
├── .env.example                   # Config template
└── pyproject.toml
```

## Contributors

Contributions are welcome. Please open an issue first to discuss what you'd like to change.

<a href="https://github.com/rootstate-dev/VaultMind/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=rootstate-dev/VaultMind" />
</a>

## License

[MIT](LICENSE)
