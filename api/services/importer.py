import json
from ingestion.creation_document import json_to_docs
import pandas as pd


class ImporterService:

    def __init__(
        self
    ):
        self

    def process(self, payload):

        docs = json_to_docs(payload)

        return docs