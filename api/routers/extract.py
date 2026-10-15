from fastapi import APIRouter, UploadFile, File, Depends, Form
from fastapi.responses import FileResponse
from services.extracter import ExtracterService
from dependencies.docling import get_document_converter
import pandas as pd
from dependencies.rag import get_qdrant
from core.vector_store import Qdrant_vs

router = APIRouter(prefix="/extract_doc", tags=["Generator"])

# @router.post("/extract")
# async def extract(
#     pdf_files: list[UploadFile] = File(...),
#     converter = Depends(get_document_converter),
#     qdrant: Qdrant_vs = Depends(get_qdrant),
# ) -> FileResponse:
#     service = ExtracterService(converter, qdrant)
#     results, final_df = await service.extract(pdf_files)
#     final_df = final_df.astype(object)
#     final_df = final_df.where(pd.notna(final_df), None)

#     return {
#         "results": results,
#         "final_df": final_df.to_dict(orient="records"),
#     }

@router.post("/extract")
async def extract(
    pdf_files: list[UploadFile] = File(...),
    converter = Depends(get_document_converter),
    qdrant: Qdrant_vs = Depends(get_qdrant),
) -> FileResponse:
    service = ExtracterService(converter, qdrant)
    results, final_df = await service.fitz_extract_per_object(pdf_files)

    return {
        "results": results,
        "final_df": final_df.to_dicts(),
    }