from pathlib import Path
from core.vector_store import Qdrant_vs


BASE_DIR = Path(__file__).resolve().parent
CLIENT_PATH = BASE_DIR / "langchain_qdrant2"

qdrant = Qdrant_vs(
    client_path=CLIENT_PATH
)


def get_qdrant() -> Qdrant_vs:
    return qdrant