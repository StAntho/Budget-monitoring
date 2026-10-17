from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class Transaction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: date | None = None
    date_valeur: date | None = None

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