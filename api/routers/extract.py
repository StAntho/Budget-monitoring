from fastapi import APIRouter, UploadFile, File, Depends, Form
from fastapi.responses import FileResponse
from services.extracter import ExtracterService
from dependencies.docling import get_document_converter
import pandas as pd

router = APIRouter(prefix="/extract_doc", tags=["Generator"])

@router.post("/extract")
async def extract(
    pdf_files: list[UploadFile] = File(...),
    converter = Depends(get_document_converter)
) -> FileResponse:
    service = ExtracterService(converter)
    results, final_df = await service.extract(pdf_files)
    final_df = final_df.astype(object)
    final_df = final_df.where(pd.notna(final_df), None)

    return {
        "results": results,
        "final_df": final_df.to_dict(orient="records"),
    }