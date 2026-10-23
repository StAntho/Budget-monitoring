from parsers.banks.current_bank import CurrentBankParser
from extraction.pdf_extractor import ExtractedDocument
from parsers.base import BaseParser


class ParserRegistry:

    def __init__(
        self,
        parsers: list[BaseParser] | None = None,
    ):
        self.parsers = (parsers 
        if parsers is not None
        else [
            CurrentBankParser(),
        ])

    def register(
        self,
        parser: BaseParser,
    ) -> None:
        self.parsers.append(parser)

    def select(
        self,
        document: ExtractedDocument,
    ) -> BaseParser:

        for parser in self.parsers:
            if parser.can_parse(document):
                return parser

        raise ValueError(
            f"Aucun parser compatible avec {document.filename}."
        )