from pathlib import Path
from ingestion.ocr import *
from fastapi import UploadFile
from docling.document_converter import DocumentConverter
from services.importer import ImporterService

class ExtracterService:
    EXTRACTED_DIR = Path("extractions")
    OUTPUT_MD_DIR = Path("markdown")

    def __init__(
        self,
        converter:DocumentConverter,
        qdrant=None
    ):
        self.converter = converter
        self.EXTRACTED_DIR.mkdir(exist_ok=True),
        self.OUTPUT_MD_DIR.mkdir(exist_ok=True),
        self.qdrant = qdrant

    async def extract(self, files: list[UploadFile]) -> dict:
        results = []
        all_dataframes = []

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

                df = save_tables(
                    filename,
                    markdown_text,
                    self.EXTRACTED_DIR,
                )

                if not df.empty:
                    df["filename"] = pdf_file.filename

                    all_dataframes.append(df)

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
            
        if all_dataframes:
            final_df = pd.concat(
                all_dataframes,
                ignore_index=True
            )
        else:
            final_df = pd.DataFrame()

        service = ImporterService(self.qdrant)
        final_df["Sous-catégorie"] = final_df.apply(
            lambda row: service.request_vs_r1(
                payload={"query": row.iloc[2], "collection": "test_embedding"}
            ),
            axis=1,
        )

        return results, final_df