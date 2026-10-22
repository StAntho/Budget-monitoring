import re
from parsers.generic.line_reconstructor import group_words_by_line, get_zone_text
from parsers.generic.date_parser import parse_dates, to_iso_date
from parsers.generic.amount_parser import parse_amount_cents
from extraction.pdf_extractor import ExtractedDocument, ExtractedWord
from schemas.transaction import Transaction
from parsers.generic.bank_statement_parser import StatementParser
from parsers.generic.column_layout import ColumnLayout

CURRENT_BANK_LAYOUT = ColumnLayout(
    date=(45, 80),
    date_valeur=(80, 132),
    operation=(132, 400),
    debit=(400, 470),
    credit=(470, 556),
)


class CurrentBankParser:
    def can_parse(self, document: ExtractedDocument) -> bool:
        return True

    def parse(
        self,
        document: ExtractedDocument,
    ) -> list[Transaction]:

        transactions = []

        for page in document.pages:
            transactions.extend(
                self.parse_page(
                    words=page.words,
                    page_number=page.page_number,
                )
            )

        return transactions


    def parse_page(
        self,
        words: list[ExtractedWord],
        page_number: int,
    ) -> list[Transaction]:

        lines = group_words_by_line(words)

        transactions = []

        for line in lines:
            operation_date, value_date = parse_dates(line)

            if not operation_date:
                continue

            operation = get_zone_text(
                line,
                CURRENT_BANK_LAYOUT.operation,
            )

            debit = parse_amount_cents(
                get_zone_text(line, CURRENT_BANK_LAYOUT.debit)
            )

            credit = parse_amount_cents(
                get_zone_text(line, CURRENT_BANK_LAYOUT.credit)
            )

            transaction = Transaction(
                date=operation_date,
                date_valeur=to_iso_date(value_date),
                operation=operation,
                debit_cents=debit,
                credit_cents=credit,
                source_page=page_number,
                status="needs_review",
            )

            transactions.append(transaction)

        return transactions

