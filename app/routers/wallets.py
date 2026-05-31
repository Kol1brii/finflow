from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas import wallets as schema
from app.services.wallets import WalletService

router = APIRouter(prefix="/wallets", tags=["wallets"])

@router.post("/create_wallet", response_model=schema.WalletResponse, status_code=201)
def create_wallet(create: schema.WalletCreateRequest, db: Session = Depends(get_db)):
    return WalletService.create_wallet(create=create, db=db)

@router.get("/all_wallets")
def check_wallets(db: Session = Depends(get_db)):
    return WalletService.check_wallets(db=db)

@router.get("/{wallet_number}/balance")
def check_balance(wallet_number: str, db: Session = Depends(get_db)):
    return WalletService.check_balance(wallet_number=wallet_number, db=db)

@router.post("/{wallet_number}/income", status_code=201)
def add_income(wallet_number: str, request: schema.OperationRequest, db: Session = Depends(get_db)):
    return WalletService.add_income(
        wallet_number=wallet_number,
        request=request,
        db=db
    )

@router.post("/{wallet_number}/expense", status_code=201)
def add_expense(wallet_number: str, request: schema.OperationRequest, db: Session = Depends(get_db)):
    return WalletService.add_expense(
        wallet_number=wallet_number,
        request=request,
        db=db
    )