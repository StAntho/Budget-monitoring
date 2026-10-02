from functools import lru_cache
from docling.document_converter import DocumentConverter

@lru_cache(maxsize=1)
def get_document_converter() -> DocumentConverter:
    return DocumentConverter()