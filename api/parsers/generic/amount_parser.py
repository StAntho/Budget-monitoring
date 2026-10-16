import re
from decimal import Decimal, InvalidOperation

AMOUNT_PATTERN = re.compile(
    r"-?\d[\d \u00a0]*(?:,\d{2})"
)


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
