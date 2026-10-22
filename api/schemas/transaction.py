from datetime import datetime, date as Date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class Transaction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: Date | str | None = None
    date_valeur: Date | None = None

    operation: str

    debit_cents: int | None = None
    credit_cents: int | None = None

    devise: str = "EUR"

    source_page: int | None = None
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    status: Literal[
        "validated",
        "needs_review",
    ] = "needs_review"


    @field_validator("date", mode="before")
    @classmethod
    def validate_operation_date(cls, value):
        if value is None or isinstance(value, Date):
            return value

        if isinstance(value, str):
            value = value.strip()

            try:
                datetime.strptime(value, "%d/%m")
                return value
            except ValueError:
                pass

            for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue

        raise ValueError("Format de date d'opération invalide")