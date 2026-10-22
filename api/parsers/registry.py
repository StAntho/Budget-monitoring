from parsers.banks.current_bank import CurrentBankParser
from extraction.pdf_extractor import ExtractedDocument
from parsers.generic.bank_statement_parser import StatementParser


class ParserRegistry:

    def __init__(
        self,
        parsers: list[StatementParser] | None = None,
    ):
        self.parsers = parsers or [
            CurrentBankParser(),
        ]

    def register(
        self,
        parser: StatementParser,
    ) -> None:
        self.parsers.append(parser)

    def select(
        self,
        document: ExtractedDocument,
    ) -> StatementParser:

        for parser in self.parsers:
            if parser.can_parse(document):
                return parser

        raise ValueError(
            f"Aucun parser compatible avec {document.filename}."
        )