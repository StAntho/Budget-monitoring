from abc import ABC, abstractmethod
from extraction.pdf_extractor import ExtractedDocument
from schemas.transaction import Transaction


class BaseParser(ABC):

    @abstractmethod
    def can_parse(
        self,
        document: ExtractedDocument,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def parse(
        self,
        document: ExtractedDocument,
    ) -> list[Transaction]:
        raise NotImplementedError