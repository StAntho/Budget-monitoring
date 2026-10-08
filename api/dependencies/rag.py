from pathlib import Path
from core.vector_store import Qdrant_vs


qdrant = Qdrant_vs(
    client_path=Path("./langchain_qdrant")
)


def get_qdrant() -> Qdrant_vs:
    return qdrant