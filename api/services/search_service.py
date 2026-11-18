from core.vector_store import Qdrant_vs

class SearchService:
    def __init__(
        self,
        qdrant: Qdrant_vs
    ):
        self.qdrant = qdrant

    
    def get_datas(self):
        collections = self.qdrant.get_collections()
        return collections


    def request_vs(self, payload):
        query = payload.get("query")

        if not isinstance(query, str) or not query.strip():
            return []
        
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
                "finalite": r.metadata['finalite'],
            }
        return {
            "sous_cat": None,
            "categorie": None,
            "sub_cat": None,
            "finalite": None,
        }


    def request_hybrid(
        self, 
        payload
    ):
        query = payload.get("query")
        if not isinstance(query, str) or not query.strip():
            return None
        vector_store = self.qdrant.get_vectorstore(payload['collection'])
        retrieve = self.qdrant.hybrid_search(
            collection=payload['collection'],
            query=payload['query'],
            who='Anto',
            limit=1
        )
            
        for r in retrieve:
            payload = r.payload or {}
            metadata = payload.get("metadata", payload)
            return {
                "sous_cat": metadata.get("sous_cat"),
                "categorie": metadata.get("categorie"),
                "sub_cat": metadata.get("sub_cat"),
                "finalite": metadata.get("finalite"),
            }

        return {
            "sous_cat": None,
            "categorie": None,
            "sub_cat": None,
            "finalite": None,
        }


    def request_dense_metadata(self, payload):
        query = payload.get("query")

        if not isinstance(query, str) or not query.strip():
            return {
                "sous_cat": None,
                "categorie": None,
                "sub_cat": None,
                "finalite": None
            }

        results = self.qdrant.dense_metadata_search(
            collection=payload["collection"],
            query=query,
            metadata_query=payload.get("metadata_query"),
            metadata_filters=payload.get("metadata_filters"),
            query_weight=payload.get("query_weight", 0.8),
            metadata_weight=payload.get("metadata_weight", 0.2),
            limit=payload.get("limit", 1)
        )

        if not results:
            return {
                "sous_cat": None,
                "categorie": None,
                "sub_cat": None,
                "finalite": None
            }

        point = results[0]

        metadata = point.payload.get("metadata", {})

        return {
            "sous_cat": metadata.get("sous_cat"),
            "categorie": metadata.get("categorie"),
            "sub_cat": metadata.get("sub_cat"),
            "finalite": metadata.get("finalite")
        }