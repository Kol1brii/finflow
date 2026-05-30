from fastapi import FastAPI
from app.routers import wallets, transactions
from contextlib import asynccontextmanager
from app.database.connection import Base, engine

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