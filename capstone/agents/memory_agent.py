from pathlib import Path

try:
    from ..memory.store import MemoryStore
except ImportError:
    from memory.store import MemoryStore


def get_memory_store() -> MemoryStore:
    return MemoryStore(Path(__file__).resolve().parent.parent / "storage" / "memory.db")
