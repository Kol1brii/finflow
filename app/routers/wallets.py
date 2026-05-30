from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.utils.luhn import generate_luhn_number
import uuid
from ..database.connection import get_db, WalletsORM, TransactionsHistoryORM

router = APIRouter(prefix="/wallets", tags=["wallets"])

class WalletCreateRequest(BaseModel):
    name: str
    balance: Decimal | None = 0

class WalletResponse(BaseModel):  # Pydantic класс
    id: uuid.UUID
    wallet_number: str = Field(min_length=16, max_length=16, pattern=r"^\d{16}$") # Валидация номера карты в диапазоне 16 символов с паттерном
    name: str
    balance: Decimal   # Аналог Float, но без мелкой погрешности в результате

    class Config:   # Позволяет pydantic классу читать sqlalchemy элементы
        from_attributes = True

class OperationRequest(BaseModel):  # Класс для валидации интервала прибавленной суммы amount в функции receive_money
    amount: Decimal = Field(default=None, gt=0, le=100_000)
    description: str | None = None



@router.post("/create_wallet", response_model=WalletResponse, status_code=201)
def create_wallet(create: WalletCreateRequest, db: Session = Depends(get_db)):
    new_wallet_id = uuid.uuid4()
    new_wallet_number = generate_luhn_number(16)
    wallet = WalletsORM(
        id=new_wallet_id,
        wallet_number=new_wallet_number,
        name=create.name,
        balance=create.balance
    )
    db.add(wallet)
    db.commit()
    return wallet

@router.get("/all_wallets")
def check_wallets(db: Session = Depends(get_db)):
    wallets_from_db = db.scalars(select(WalletsORM)).all()
    return wallets_from_db

@router.get("/{wallet_number}/balance")
def check_balance(wallet_number: str, db: Session = Depends(get_db)):
    statement = (   # Синтаксический сахар
        select(WalletsORM)
        .where(WalletsORM.wallet_number==wallet_number)
    )

    wallet = db.scalars(statement).one_or_none()
    if wallet is None:
        raise HTTPException(404, f"Wallet '{wallet_number}' not found")
    return wallet.balance

@router.post("/{wallet_number}/income")
def add_income(wallet_number: str, request: OperationRequest, db: Session = Depends(get_db)):
    statement = (  # Синтаксический сахар
        select(WalletsORM)
        .where(WalletsORM.wallet_number == wallet_number)
        .with_for_update()
    )

    wallet = db.scalars(statement).one_or_none()
    if wallet is None:
        raise HTTPException(404, f"Wallet '{wallet_number}' not found")
    wallet.balance += request.amount

    transaction_log = TransactionsHistoryORM(
        wallet_id=wallet.id,
        status="add income",
        amount=request.amount,
        description=request.description,
        balance=wallet.balance
    )

    db.add(transaction_log)
    db.commit()
    db.refresh(transaction_log)

    return {
            "status": f"Credited {request.amount}",
            "wallet_id": wallet.id,
            "amount": request.amount,
            "description": request.description,
            "Total amount": wallet.balance,
            "date": transaction_log.date.isoformat(),
        }

@router.post("/{wallet_number}/expense")
def add_expense(wallet_number: str, request: OperationRequest, db: Session = Depends(get_db)):
    statement = (  # Синтаксический сахар
        select(WalletsORM)
        .where(WalletsORM.wallet_number == wallet_number)
        .with_for_update()
    )

    wallet = db.scalars(statement).one_or_none()
    if wallet is None:
        raise HTTPException(404, f"Wallet '{wallet_number}' not found")
    wallet.balance -= request.amount

    transaction_log = TransactionsHistoryORM(
        wallet_id=wallet.id,
        status="add expense",
        amount=request.amount,
        description=request.description,
        balance=wallet.balance
    )

    db.add(transaction_log)
    db.commit()
    db.refresh(transaction_log)

    return {
        "status": f"Credited {request.amount}",
        "wallet_id": wallet.id,
        "amount": request.amount,
        "description": request.description,
        "Total amount": wallet.balance,
        "date": transaction_log.date.isoformat(),
    }