import os
import re
from datetime import datetime, timezone
from pathlib import Path
import frontmatter
from ..config import config


def get_all_paths() -> list[str]:
    vault = Path(config.vault_path)
    return [
        str(p.relative_to(vault)).replace("\\", "/")
        for p in vault.rglob("*.md")
    ]


def get_content(relative_path: str) -> str | None:
    full = Path(config.vault_path) / relative_path
    if not full.exists():
        return None
    return full.read_text(encoding="utf-8")


def write_note(title: str, content: str, tags: list[str]) -> str:
    parts = [p.strip() for p in title.split('/') if p.strip()]
    slugged = []
    for part in parts:
        s = re.sub(r'[^a-z0-9\s-]', '', part.lower())
        s = re.sub(r'\s+', '_', s).strip('_')
        slugged.append(s)

    *folders, slug = slugged
    file_name = f"{slug}.md"
    full_path = Path(config.vault_path) / Path(*folders, file_name) if folders else Path(config.vault_path) / file_name

    i = 2
    while full_path.exists():
        full_path = full_path.parent / f"{slug}_{i}.md"
        i += 1

    now = datetime.now(timezone.utc).isoformat()
    fm = frontmatter.Post(
        content,
        title=title,
        tags=tags,
        created=now,
        updated=now,
    )

    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(frontmatter.dumps(fm), encoding="utf-8")

    return str(full_path.relative_to(config.vault_path)).replace("\\", "/")
