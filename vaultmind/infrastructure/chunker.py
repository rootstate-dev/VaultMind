import re
import frontmatter
from ..core.models import Chunk
from ..config import config


def chunk_file(file_path: str, relative_path: str) -> list[Chunk]:
    with open(file_path, encoding="utf-8") as f:
        post = frontmatter.load(f)

    text = post.content.strip()
    sections = _split_by_headings(text)

    chunks = []
    idx = 0
    for heading, section_text in sections:
        if not section_text.strip():
            continue
        sub = _split_by_size(section_text, heading, relative_path, idx)
        chunks.extend(sub)
        idx += len(sub)

    return chunks


def _split_by_headings(text: str) -> list[tuple[str, str]]:
    # Split on any heading level: #, ##, ###, ####
    pattern = re.compile(r'^(#{1,4} .+)$', re.MULTILINE)
    parts = pattern.split(text)

    sections = []
    i = 0

    if parts[0].strip():
        sections.append(("", parts[0].strip()))
    i = 1

    while i < len(parts):
        heading = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        sections.append((heading, body))
        i += 2

    return sections


def _split_by_size(text: str, heading: str, file_path: str, start_idx: int) -> list[Chunk]:
    max_chars = config.max_chunk_chars
    overlap = config.chunk_overlap_chars
    chunks = []

    prefix = f"[{heading}]\n" if heading else ""

    if len(text) <= max_chars:
        chunks.append(Chunk(
            id=f"{file_path}::{start_idx}",
            file_path=file_path,
            heading=heading,
            content=prefix + text,
            chunk_index=start_idx,
        ))
        return chunks

    start = 0
    idx = start_idx
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(Chunk(
            id=f"{file_path}::{idx}",
            file_path=file_path,
            heading=heading,
            content=prefix + text[start:end],
            chunk_index=idx,
        ))
        idx += 1
        start += max_chars - overlap

    return chunks
