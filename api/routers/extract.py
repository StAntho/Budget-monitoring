from fastapi import APIRouter, UploadFile, File, Depends, Body
from fastapi.responses import FileResponse
from services.extracter import ExtracterService
from dependencies.docling import get_document_converter
import pandas as pd
from dependencies.rag import get_qdrant
from core.vector_store import Qdrant_vs

router = APIRouter(prefix="/extract_doc", tags=["Generator"])

@router.post("/extract")
async def extract(
    pdf_files: list[UploadFile] = File(...),
    converter = Depends(get_document_converter),
    qdrant: Qdrant_vs = Depends(get_qdrant),
) -> FileResponse:
    service = ExtracterService(converter=converter, qdrant=qdrant)
    return await service.fitz_extract_per_object(pdf_files)


@router.post("/validate")
async def validate_import(
    payload: dict = Body(...),
    converter = Depends(get_document_converter),
    qdrant: Qdrant_vs = Depends(get_qdrant),
):
    service = ExtracterService(converter=converter, qdrant=qdrant)
    return await service.validate_extract_df(payload)