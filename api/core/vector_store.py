import os
from dotenv import load_dotenv
from embedding.embedder import embedding
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from pathlib import Path

load_dotenv()
EMBEDDING_MODEL_NAME_ST = os.getenv('ST_EMBEDDING_MODEL')

class Qdrant_vs():

    def __init__(
        self,
        client_path:Path
    ):
        self.client = QdrantClient(path=client_path, prefer_grpc=False)

    def create_vectorestore(
        self,
        collection_name:str
    ):
        vectorstore = self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
        return vectorstore
    
        
    def get_vectorstore(
        collection: str,
        db_path: str,     
    ):
        embedder = embedding(EMBEDDING_MODEL_NAME_ST)
        qdrant = QdrantVectorStore.from_existing_collection(
            embedding=embedder,
            collection_name=collection,
            path=db_path,
        )

        return qdrant

    def get_collections(self):
        collections = self.client.get_collections()
        return collections
    
    def add_documents(
        vector_store,
        token_split_texts
    ):
        try:
            vector_store.add_documents(token_split_texts)
            response = {"code": 200, "message": "Ajout de documents réussi"}
        except Exception as e:
            return f"L'ajout de document a échoué - Erreur: {e}" 