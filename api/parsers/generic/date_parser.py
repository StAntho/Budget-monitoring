import re
from datetime import date

DATE_PATTERN = re.compile(r"^\d{2}/\d{2}$")
DATE_FULL_PATTERN = re.compile(r"^\d{2}/\d{2}/\d{4}$")

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

    return None