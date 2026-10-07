import json, os
from ingestion.creation_document import json_to_docs
from chunking.chunking import chunk_for_doc
import pandas as pd
from dotenv import load_dotenv
from embedding.embedder import embedding
from core.vector_store import Qdrant_vs
from pathlib import Path

load_dotenv()

EMBEDDING_MODEL_NAME_ST = os.getenv('ST_EMBEDDING_MODEL')

class ImporterService:

    def __init__(
        self
    ):
        self

    def process(self, payload):

        docs = json_to_docs(payload)
        print("✅ Tous les documents sont bien créés")
        chunks = chunk_for_doc(docs)
        print("✅ Chunks fait")
        embedder = embedding(EMBEDDING_MODEL_NAME_ST)
        qdrant = Qdrant_vs(
            client_path=Path("./langchain_qdrant")
        )

        vectorstore = qdrant.create_vectorestore(
            collection_name="test_embedding"
        )
        add_docs = Qdrant_vs.add_documents(vectorstore, chunks)



        return chunks