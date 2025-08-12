from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="AI Legal Drafter")
app.include_router(router)
