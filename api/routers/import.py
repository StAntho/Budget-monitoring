from fastapi import APIRouter, Body, Depends
from services.importer import ImporterService
from dependencies.rag import get_qdrant
from core.vector_store import Qdrant_vs

router = APIRouter(prefix="/import_doc", tags=["Importator"])

@router.post("/process")
def process(
    payload: dict = Body(...),
    qdrant: Qdrant_vs = Depends(get_qdrant)
):
    service = ImporterService(qdrant)
    return service.process(payload)

@router.get('/get_datas_vs')
def get_datas_vs(qdrant: Qdrant_vs = Depends(get_qdrant)):
    service = ImporterService(qdrant)
    return service.get_datas()

@router.post('/request_vs')
def request_vs(
    payload: dict = Body(...),               
    qdrant: Qdrant_vs = Depends(get_qdrant),
):
    service = ImporterService(qdrant)
    return service.request_vs(payload)