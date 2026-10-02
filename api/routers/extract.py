from fastapi import APIRouter, UploadFile, File, Depends, Form
from fastapi.responses import FileResponse
from services.extracter import ExtracterService
from dependencies.docling import get_document_converter

router = APIRouter(prefix="/extract_doc", tags=["Generator"])

@router.post("/extract")
async def extract(
    pdf_files: list[UploadFile] = File(...),
    converter = Depends(get_document_converter)
) -> FileResponse:
    service = ExtracterService(converter)
    return await service.extract(pdf_files)