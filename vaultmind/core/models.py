from dataclasses import dataclass


@dataclass
class Chunk:
    id: str
    file_path: str
    heading: str
    content: str
    chunk_index: int


@dataclass
class SearchResult:
    id: str
    document: str
    file_path: str
    heading: str
    score: float
