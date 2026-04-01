import logging
import threading
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent, FileMovedEvent
from ..services.indexer import index_file
from ..infrastructure.store import delete_by_file
from ..config import config

logger = logging.getLogger(__name__)


class VaultHandler(FileSystemEventHandler):
    def __init__(self):
        self._timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def _relative(self, path: str) -> str:
        return str(Path(path).relative_to(config.vault_path)).replace("\\", "/")

    def _debounce(self, relative_path: str, action):
        with self._lock:
            if relative_path in self._timers:
                self._timers[relative_path].cancel()
            t = threading.Timer(0.5, action, args=[relative_path])
            self._timers[relative_path] = t
            t.start()

    def on_created(self, event):
        if not isinstance(event, FileCreatedEvent) or not event.src_path.endswith(".md"):
            return
        self._debounce(self._relative(event.src_path), index_file)

    def on_modified(self, event):
        if not isinstance(event, FileModifiedEvent) or not event.src_path.endswith(".md"):
            return
        self._debounce(self._relative(event.src_path), index_file)

    def on_deleted(self, event):
        if not isinstance(event, FileDeletedEvent) or not event.src_path.endswith(".md"):
            return
        rel = self._relative(event.src_path)
        delete_by_file(rel)

    def on_moved(self, event):
        if not isinstance(event, FileMovedEvent) or not event.dest_path.endswith(".md"):
            return
        delete_by_file(self._relative(event.src_path))
        self._debounce(self._relative(event.dest_path), index_file)


_observer: Observer | None = None


def start_watcher():
    global _observer
    _observer = Observer()
    _observer.schedule(VaultHandler(), config.vault_path, recursive=True)
    _observer.start()
    logger.info("File watcher started on %s", config.vault_path)


def stop_watcher():
    if _observer:
        _observer.stop()
        _observer.join()
