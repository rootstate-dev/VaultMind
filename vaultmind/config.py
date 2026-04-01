import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    vault_path: str = field(default_factory=lambda: os.environ["VAULT_PATH"])
    chroma_path: str = field(default_factory=lambda: os.getenv("CHROMA_PATH", "chroma_db"))
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    top_k: int = field(default_factory=lambda: int(os.getenv("TOP_K", "5")))
    max_chunk_chars: int = field(default_factory=lambda: int(os.getenv("MAX_CHUNK_CHARS", "1600")))
    chunk_overlap_chars: int = field(default_factory=lambda: int(os.getenv("CHUNK_OVERLAP_CHARS", "200")))

config = Config()
