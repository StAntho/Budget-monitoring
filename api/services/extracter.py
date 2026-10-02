from pathlib import Path
from ingestion.ocr import *
from fastapi import UploadFile
from docling.document_converter import DocumentConverter

class ExtracterService:
    EXTRACTED_DIR = Path("extractions")
    OUTPUT_MD_DIR = Path("markdown")

    def __init__(
        self,
        converter:DocumentConverter
    ):
        self.converter = converter
        self.EXTRACTED_DIR.mkdir(exist_ok=True),
        self.OUTPUT_MD_DIR.mkdir(exist_ok=True)

    async def extract(self, files: list[UploadFile]) -> dict:
        results = []

        for pdf_file in files:
            print(pdf_file.filename)
            try:
                doc_converter = await convert_pdf_to_docling(
                    pdf_file,
                    self.converter,
                )

                filename = Path(pdf_file.filename)

                markdown_text = doc_converter.document.export_to_markdown(page_break_placeholder="<!-- page break -->")

                markdown_path = self.OUTPUT_MD_DIR / f"{filename}.md"
                markdown_path.write_text(
                    markdown_text,
                    encoding="utf-8",
                )

                save_tables(
                    markdown_text,
                    self.EXTRACTED_DIR,
                )

                results.append({
                    "filename": pdf_file.filename,
                    "status": "success",
                    "markdown_file": markdown_path.name,
                    "message": "Document extrait avec succès",
                })

            except Exception as e:
                results.append({
                    "filename": pdf_file.filename,
                    "status": "error",
                    "message": str(e),
                })
            
        return results