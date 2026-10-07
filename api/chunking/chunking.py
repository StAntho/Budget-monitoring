from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter

def chunk_for_doc(
        docs, 
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        model_name="sentence-transformers/all-distilroberta-v1",
    ):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunked_docs = []
    for doc in docs:
        for chunk in splitter.split_text(doc.page_content):
            chunked_docs.append(Document(
                page_content=chunk,
                metadata=doc.metadata
            ))

    token_splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=chunk_overlap, tokens_per_chunk=chunk_size, model_name=model_name
    )
    token_split_texts = []
    for text in chunked_docs:
        token_split_texts.extend(
            token_splitter.split_documents([text])
        )

    return token_split_texts