import re
from datetime import date
from decimal import Decimal, InvalidOperation


DATE_X = (45, 80)
DATE_VALEUR_X = (80, 132)
OPERATION_X = (132, 400)
DEBIT_X = (400, 470)
CREDIT_X = (470, 556)

DATE_PATTERN = re.compile(r"^\d{2}/\d{2}$")
DATE_FULL_PATTERN = re.compile(r"^\d{2}/\d{2}/\d{4}$")

AMOUNT_PATTERN = re.compile(
    r"-?\d[\d \u00a0]*(?:,\d{2})"
)


def group_words_by_line(
    words: list,
    tolerance: float = 4.0,
) -> list[list]:

    sorted_words = sorted(
        words,
        key=lambda word: (word[1], word[0]),
    )

    lines = []

    for word in sorted_words:
        y0 = word[1]

        if (
            lines
            and abs(lines[-1]["y"] - y0) <= tolerance
        ):
            lines[-1]["words"].append(word)

            # Mettre à jour le centre vertical de la ligne
            ys = [
                w[1]
                for w in lines[-1]["words"]
            ]

            lines[-1]["y"] = sum(ys) / len(ys)

        else:
            lines.append({
                "y": y0,
                "words": [word],
            })

    return [
        sorted(
            line["words"],
            key=lambda word: word[0],
        )
        for line in lines
    ]


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


def parse_amount_cents(
    value: str,
) -> int | None:

    if not value:
        return None

    value = (
        value
        .replace("\u00a0", " ")
        .replace("€", "")
        .strip()
    )

    match = AMOUNT_PATTERN.search(value)

    if not match:
        return None

    normalized = (
        match.group()
        .replace(" ", "")
        .replace(",", ".")
    )

    try:
        amount = Decimal(normalized)
        return int(amount * 100)
    except (InvalidOperation, ValueError):
        return None


def parse_dates(
    words: list,
) -> tuple[str | None, str | None]:

    operation_date = None
    value_date = None

    for word in words:
        text = word[4].strip()

        if DATE_FULL_PATTERN.fullmatch(text):
            value_date = text

        elif DATE_PATTERN.fullmatch(text):
            operation_date = text

    return operation_date, value_date


def to_iso_date(
    operation_date: str | None,
    value_date: str | None,
) -> str | None:

    if value_date:
        parsed = date.fromisoformat(
            f"{value_date[6:10]}-"
            f"{value_date[3:5]}-"
            f"{value_date[0:2]}"
        )

        return parsed.isoformat()

    # Sans année connue, nous ne fabriquons pas de date.
    # Une autre règle pourra être ajoutée ultérieurement.
    return None


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
