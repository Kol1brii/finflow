from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas.transactions import TransferResponse, TransferRequest
from app.services.transactions import WalletService
from ..database.connection import get_db
from decimal import Decimal

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

@router.get("/history")
def check_transactions(db: Session = Depends(get_db)):
    return WalletService.check_transactions(db=db)

@router.post("/transfer", response_model=TransferResponse, status_code=201)
def transfer(request: TransferRequest, db: Session = Depends(get_db)):
    return WalletService.transfer(
        from_wallet_number=request.from_wallet_number,
        to_wallet_number=request.to_wallet_number,
        amount=request.amount,
        description=request.description,
        db=db
    )