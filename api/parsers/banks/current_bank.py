import re
from parsers.generic.line_reconstructor import group_words_by_line
from parsers.generic.date_parser import parse_dates, to_iso_date
from parsers.generic.amount_parser import parse_amount_cents


DATE_X = (45, 80)
DATE_VALEUR_X = (80, 132)
OPERATION_X = (132, 400)
DEBIT_X = (400, 470)
CREDIT_X = (470, 556)



def get_zone_text(
    words: list,
    x_range: tuple[float, float],
) -> str:

    x_min, x_max = x_range

    selected = [
        word
        for word in words
        if word[0] >= x_min and word[2] <= x_max
    ]

    selected.sort(key=lambda word: word[0])

    return " ".join(
        word[4]
        for word in selected
    ).strip()



class CurrentBankParser:
    def can_parse(self, document) -> bool:
        return True

    def parse_page(
        self,
        words: list,
        page_number: int,
    ) -> list[dict]:

        lines = group_words_by_line(words)

        transactions = []

        for line in lines:
            operation_date, value_date = parse_dates(line)
            if not operation_date:
                continue

            operation = get_zone_text(
                line,
                OPERATION_X,
            )
            debit = parse_amount_cents(
                get_zone_text(line, DEBIT_X)
            )
            credit = parse_amount_cents(
                get_zone_text(line, CREDIT_X)
            )
            transactions.append({
                "date_brute": operation_date,
                "date_valeur_brute": value_date,
                "date": to_iso_date(
                    operation_date,
                    value_date,
                ),
                "date_valeur": value_date,
                "operation": operation,
                "debit_cents": debit,
                "credit_cents": credit,
                "source_page": page_number,
            })

        return transactions

