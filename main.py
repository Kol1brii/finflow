from fastapi import FastAPI
from app.routers import wallets, transactions
#uvicorn main:app --reload


app = FastAPI(title="finflow")
app.include_router(wallets.router)
app.include_router(transactions.router)

@app.get("/")
def root():
    return {"Message": "Стартуем!"}