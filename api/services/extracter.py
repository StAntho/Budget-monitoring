from pathlib import Path
from ingestion.ocr import *
from fastapi import UploadFile
from docling.document_converter import DocumentConverter
from services.importer import ImporterService
import fitz, re

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


    async def fitz_extract_per_object(self, files: list[UploadFile]) -> dict:
        for pdf_file in files:
            pdf_bytes = await pdf_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            page_blocks = []
            for page_number in range(len(doc)):
                page = doc[page_number]
                blocks_md = []
                table_bboxes = []
                table_items = []
                for table in page.find_tables():                                                                                                                            
                    table_bboxes.append(table.bbox)                                                                                                                         
                    rows = table.extract()                                                                                                                                  
                    if not rows:
                        continue
                    def _cell(c):
                        return str(c or "").strip().replace('\n', '<br>')
                    headers = [_cell(h) for h in rows[0]]                                                                                                                   
                    lines = [
                        "| " + " | ".join(headers) + " |",                                                                                                                  
                        "| " + " | ".join("---" for _ in headers) + " |",
                    ]                                                                                                                                                       
                    for row in rows[1:]:
                        lines.append("| " + " | ".join(_cell(c) for c in row) + " |")                                                                                       
                    
                    table_items.append((table.bbox[1], "\n".join(lines)))                                                                                                   
            
                table_items.sort(key=lambda item: item[0])                                                                                                                    
                blocks_md = [content for _, content in table_items]

                page_blocks.append("\n\n".join(blocks_md))

            doc.close()

            full_markdown = "\n\n<!-- page break -->\n\n".join(page_blocks)


            chunks = [full_markdown] if full_markdown.strip() else []

            saved = []
            current_page = page
            for chunk_num, content in enumerate(chunks, start=1):
                start_pdf_page = 1
                break_count    = content.count('<!-- page break -->')
                end_pdf_page   = len(page_blocks)
                current_page   = end_pdf_page + 1

                content  = f'<!-- pdf pages {start_pdf_page}-{end_pdf_page} -->\n\n' + content
                out_path = self.OUTPUT_MD_DIR / f"{pdf_file.filename.rsplit('.', 1)[0]}_chunk_{chunk_num}_pages_{start_pdf_page}-{end_pdf_page}.md"
                out_path.write_text(content, encoding='utf-8')
                saved.append(out_path)
                print(f'  Chunk {chunk_num} → {out_path.name} (pdf pages {start_pdf_page}-{end_pdf_page})')


            return saved