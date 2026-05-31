from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services.transactions import WalletService
from ..database.connection import get_db

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

@router.get("/")
def check_transactions(db: Session = Depends(get_db)):
    return WalletService.check_transactions(db=db)