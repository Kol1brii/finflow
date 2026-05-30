from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.connection import TransactionsHistoryORM, get_db
from sqlalchemy import select

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

@router.get("/")
def check_transactions(db: Session = Depends(get_db)):
    transactions = db.scalars(select(TransactionsHistoryORM)).all()
    return transactions