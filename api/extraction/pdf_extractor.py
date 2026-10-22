from dataclasses import dataclass
from pathlib import Path
import pymupdf


@dataclass
class ExtractedWord:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float


@dataclass
class ExtractedTable:
    page_number: int
    bbox: tuple[float, float, float, float]
    rows: list[list[str]]


@dataclass
class ExtractedPage:
    page_number: int
    words: list[ExtractedWord]
    tables: list[ExtractedTable]


@dataclass
class ExtractedDocument:
    filename: str
    pages: list[ExtractedPage]


class PdfExtractor:
    def extract(self, pdf_path: Path) -> ExtractedDocument:
        with pymupdf.open(pdf_path) as doc:
            return self._extract_document(
                doc,
                filename=pdf_path.name,
            )

    def extract_bytes(
        self,
        pdf_bytes: bytes,
        filename: str,
    ) -> ExtractedDocument:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
            return self._extract_document(
                doc,
                filename=filename,
            )
        

    def _extract_document(
        self,
        doc,
        filename: str,
    ) -> ExtractedDocument:
        pages = []

        for page_number, page in enumerate(doc, start=1):
            words = [
                ExtractedWord(
                    text=word[4],
                    x0=word[0],
                    y0=word[1],
                    x1=word[2],
                    y1=word[3],
                )
                for word in page.get_text("words")
            ]

            tables = []

            for table in page.find_tables().tables:
                rows = table.extract()

                tables.append(
                    ExtractedTable(
                        page_number=page_number,
                        bbox=tuple(table.bbox),
                        rows=rows,
                    )
                )

            pages.append(
                ExtractedPage(
                    page_number=page_number,
                    words=words,
                    tables=tables,
                )
            )

        return ExtractedDocument(
            filename=filename,
            pages=pages,
        )