from fastapi import APIRouter
from services.analyser import AnalyserService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

analyser_service = AnalyserService()

@router.get("/monthly-expenses")
def get_monthly_expenses():
    df = analyser_service.get_monthly_expenses()
    return df.to_dicts()
