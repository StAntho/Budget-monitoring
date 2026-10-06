from fastapi import APIRouter, Body
from services.importer import ImporterService
from dependencies.docling import get_document_converter
import pandas as pd

router = APIRouter(prefix="/import_doc", tags=["Importator"])

@router.post("/process")
def process(
    payload: dict = Body(...),
):
    service = ImporterService()
    return service.process(payload)