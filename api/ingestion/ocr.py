from pathlib import Path
from fastapi import UploadFile
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import DocumentStream
from io import BytesIO
import pandas as pd
from io import StringIO
from utils.manage_markdown import markdown_table_to_df


async def convert_pdf_to_docling(
        pdf_file: UploadFile,
        converter: DocumentConverter,
    ):
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = 2
    pipeline_options.generate_picture_images = True
    pipeline_options.generate_page_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    content = await pdf_file.read()
    source = DocumentStream(
        name=pdf_file.filename or "document.pdf",
        stream=BytesIO(content),
    )

    return doc_converter.convert(source)


def extract_context_and_table(lines: List[str], table_index: int):
    """
    Extract context and table
    """
    table_lines = []
    i = table_index

    while(i<len(lines)) and (lines[i].startswith('|')):
        table_lines.append(lines[i])
        i = i + 1
    
    start = max(0, table_index-2)
    context_lines = lines[start: table_index]

    content = '\n'.join(context_lines) + '\n\n' + '\n'.join(table_lines)

    return content, i


def extract_tables_with_context(markdown_text: str):
    """
    Find all tables and extract
    """
    lines = markdown_text.split('\n')
    lines = [line for line in lines if line.strip()]
    tables = []
    current_page = 1
    table_num = 1
    i = 0

    while(i<len(lines)):
        if "<!-- page break -->" in lines[i]:
            current_page = current_page + 1
            i = i + 1
            continue

        if lines[i].startswith('|') and lines[i].count('|')>1:
            content, next_i = extract_context_and_table(lines, i)

            tables.append((content, f"table_{table_num}", current_page))
            table_num = table_num + 1
            i = next_i
        else:
            i = i + 1

    return tables


def save_tables(filename: str, markdow_text, tables_dir):
    tables = extract_tables_with_context(markdow_text)
    dataframe = []

    output_dir = tables_dir / filename
    output_dir.mkdir(parents=True, exist_ok=True)

    for table_content, table_name, page_num in tables:
        content_with_page = f"**Page:** {page_num}\n\n{table_content}"

        df = markdown_table_to_df(table_content)

        if df.empty:
            continue

        df["page"] = page_num
        dataframe.append(df)

        (output_dir /f"{table_name}_page_{page_num}.md").write_text(content_with_page, encoding ='utf-8')

    if dataframe:
        return pd.concat(
            dataframe,
            ignore_index=True
        )

    return pd.DataFrame()