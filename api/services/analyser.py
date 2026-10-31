from repositories.analytics_repository import AnalyticsRepository


class AnalyserService:
    def __init__(self):
        self.repository = AnalyticsRepository()

    def get_monthly_expenses(self):
        df = self.repository.get_monthly_expenses_by_category()
        return df
