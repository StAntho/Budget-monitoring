from fastapi import FastAPI
from routers import all_routers

from dotenv import load_dotenv

load_dotenv()

## Initialisation de l'app FastAPI
app = FastAPI()

for router in all_routers: 
    app.include_router(router)