from dataclasses import dataclass

@dataclass(frozen=True)
class ColumnLayout:
    date: tuple[float, float]
    date_valeur: tuple[float, float]
    operation: tuple[float, float]
    debit: tuple[float, float]
    credit: tuple[float, float]