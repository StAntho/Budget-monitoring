import re
from datetime import date, datetime

DATE_PATTERN = re.compile(r"^\d{2}/\d{2}$")
DATE_FULL_PATTERN = re.compile(r"^\d{2}/\d{2}/\d{4}$")

def parse_dates(
    words: list,
) -> tuple[str | None, str | None]:

    operation_date = None
    value_date = None

    for word in words:
        text = word.text.strip()

        if DATE_FULL_PATTERN.fullmatch(text):
            value_date = text

        elif DATE_PATTERN.fullmatch(text):
            operation_date = text

    return operation_date, value_date


def to_iso_date(value: str | None) -> str | None:
    if not value:
        return None

    value = value.strip()

    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue

    if len(value.split("/")) == 2:
        try:
            datetime.strptime(value, "%d/%m")
            return value
        except ValueError:
            pass

    return None