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
        self,
        collection: str,  
    ):
        embedder = embedding(EMBEDDING_MODEL_NAME_ST)
        return QdrantVectorStore(
            client=self.client,
            collection_name=collection,
            embedding=embedder,
        )

    def get_collections(self):
        collections = self.client.get_collections()
        return collections
    
    def add_documents(
        self,
        vector_store,
        token_split_texts
    ):
        try:
            vector_store.add_documents(token_split_texts)
            return {
                "code": 200,
                "message": "Ajout de documents réussi",
            }
        except Exception as e:
            return {
                "code": 500,
                "message": (
                    f"L'ajout de document a échoué - Erreur: {e}"
                ),
            } 