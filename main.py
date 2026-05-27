from email.encoders import encode_base64

from fastapi import FastAPI
from sqlalchemy.orm import DeclarativeBase
from app.routers import wallets, transactions
from contextlib import asynccontextmanager
from app.database.connection import Base, engine
import asyncio
# uvicorn main:app --reload
# docker exec -it finflow-cont psql -U postgres

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan, title="finflow")
app.include_router(wallets.router)
app.include_router(transactions.router)

@app.get("/")
def root():
    return {"Message": "Стартуем!"}