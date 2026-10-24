from pathlib import Path
from ingestion.ocr import *
from fastapi import UploadFile
from docling.document_converter import DocumentConverter
from services.importer import ImporterService
import fitz, re
from parsers.banks.current_bank import CurrentBankParser
import polars as pl
from extraction.pdf_extractor import PdfExtractor
from extraction.markdown_exporter import MarkdownExporter
from parsers.registry import ParserRegistry

class ExtracterService:
    EXTRACTED_DIR = Path("extractions")
    OUTPUT_MD_DIR = Path("markdown")

    def __init__(
        self,
        converter:DocumentConverter,
        extractor: PdfExtractor | None = None,
        registry: ParserRegistry | None = None,
        markdown_exporter: MarkdownExporter | None = None,
        qdrant=None
    ):
        self.converter = converter
        self.EXTRACTED_DIR.mkdir(exist_ok=True),
        self.OUTPUT_MD_DIR.mkdir(exist_ok=True),
        self.extractor = extractor or PdfExtractor()
        self.registry = registry or ParserRegistry()
        self.markdown_exporter = (
            markdown_exporter or MarkdownExporter()
        )
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
        result = final_df.apply(
            lambda row: service.request_vs_r1(
                payload={"query": row.iloc[2], "collection": "test_embedding"}
            ),
            axis=1,
        )

        result = result.apply(
            lambda x: x if isinstance(x, dict) else {
                "sous_cat": None,
                "categorie": None,
                "sub_cat": None,
            }
        )

        final_df[["Sous-catégorie", "categorie", "Sub-categorie"]] = pd.DataFrame(
            result.tolist(),
            index=final_df.index
        )[["sous_cat", "categorie", "sub_cat"]].values

        return results, final_df


    async def fitz_extract_per_object(
        self,
        files: list[UploadFile],
    ) -> tuple[list[dict], pl.DataFrame]:
        results = []
        all_transactions = []

        for pdf_file in files:
            pdf_bytes = await pdf_file.read()
            filename = pdf_file.filename or "document.pdf"

            document = self.extractor.extract_bytes(
                pdf_bytes=pdf_bytes,
                filename=filename,
            )

            parser = self.registry.select(document)

            transactions = parser.parse(document)

            transaction_dicts = [
                transaction.model_dump(mode="json")
                for transaction in transactions
            ]

            all_transactions.extend(transaction_dicts)

            markdown_content = self.markdown_exporter.export(
                document
            )

            start_page = 1
            end_page = len(document.pages)

            output_name = (
                f"{Path(filename).stem}"
                f"_chunk_1_pages_"
                f"{start_page}-{end_page}.md"
            )

            out_path = self.OUTPUT_MD_DIR / output_name

            out_path.write_text(
                markdown_content,
                encoding="utf-8",
            )

            results.append({
                "filename": filename,
                "markdown_path": str(out_path),
                "parser": parser.__class__.__name__,
                "transactions": transaction_dicts,
            })

        schema = {
            "date": pl.String,
            "date_valeur": pl.String,
            "operation": pl.String,
            "debit_cents": pl.Int64,
            "credit_cents": pl.Int64,
            "devise": pl.String,
            "source_page": pl.Int64,
            "confidence": pl.Float64,
            "status": pl.String,
        }

        final_df = pl.DataFrame(
            all_transactions,
            schema=schema,
            strict=False,
        )

        service = ImporterService(self.qdrant)
        queries = final_df.to_series(2).to_list()
        result = [ service.request_vs_r1( 
            payload={ "query": query, "collection": "test_embedding", } 
            ) for query in queries ]

        normalized_results = [ item if isinstance(item, dict) else { "sous_cat": None, "categorie": None, "sub_cat": None, } for item in result ]

        categories_df = pl.DataFrame( 
            { 
                "Sous-catégorie": [ item.get("sous_cat") for item in normalized_results ], 
                "categorie": [ item.get("categorie") for item in normalized_results ], 
                "Sub-categorie": [ item.get("sub_cat") for item in normalized_results ], 
            } 
        )

        if final_df.height != categories_df.height: 
            raise ValueError( "Le nombre de résultats de classification " "ne correspond pas au nombre de transactions." )

        
        final_df = final_df.with_columns( 
            categories_df.get_column("Sous-catégorie"), 
            categories_df.get_column("categorie"), 
            categories_df.get_column("Sub-categorie"), 
        )

        return results, final_df