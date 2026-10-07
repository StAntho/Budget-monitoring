from langchain_huggingface import HuggingFaceEmbeddings

def embedding(model: str, device: str="cpu"):
    embedder = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-distilroberta-v1", 
        model_kwargs={"device": "cpu"},
        multi_process=False
    )

    return embedder