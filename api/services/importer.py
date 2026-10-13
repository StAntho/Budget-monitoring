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
        self,
        qdrant: Qdrant_vs
    ):
        self.qdrant = qdrant

    def process(self, payload):
        docs = json_to_docs(payload)
        print("✅ Tous les documents sont bien créés")

        chunks = chunk_for_doc(docs)
        print("✅ Chunks fait")

        vectorstore = self.qdrant.create_vectorestore(
            collection_name="test_embedding"
        )

        add_docs = self.qdrant.add_documents(
            vectorstore,
            chunks
        )

        return add_docs
    

    def get_datas(self):
        collections = self.qdrant.get_collections()
        return collections

    def request_vs(self, payload):
        vector_store = self.qdrant.get_vectorstore(payload['collection'])
        retrieves = vector_store.similarity_search(payload['query'], k=2)
        return retrieves

    def request_vs_r1(self, payload):
        query = payload.get("query")
        if not isinstance(query, str) or not query.strip():
            return None
        vector_store = self.qdrant.get_vectorstore(payload['collection'])
        retrieves = vector_store.similarity_search(payload['query'], k=1)
        
        for r in retrieves:
            return {
                "sous_cat": r.metadata['sous_cat'],
                "categorie": r.metadata['categorie'],
                "sub_cat": r.metadata['sub_cat'],
            }
        return {
            "sous_cat": None,
            "categorie": None,
            "sub_cat": None,
        }