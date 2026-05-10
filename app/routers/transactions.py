from fastapi import APIRouter
from .wallets import TRANSACTION_HISTORY

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

@router.get("/")
def check_transactions():
    return TRANSACTION_HISTORY