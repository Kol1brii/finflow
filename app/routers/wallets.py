from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, condecimal
from decimal import Decimal
from sqlalchemy import select

from sentry_sdk.session import Session
from sqlalchemy.orm import Session

from app.utils.luhn import generate_luhn_number, validate_luhn
import uuid

from ..database.connection import get_db, WalletsORM

router = APIRouter(prefix="/wallets", tags=["wallets"])

TRANSACTION_HISTORY = []   # История транзакций

class WalletCreateRequest(BaseModel):
    name: str
    balance: Decimal | None = 0

class WalletResponse(BaseModel):  # Pydantic класс
    status: str | None = None
    wallet_id: uuid.UUID
    wallet_number: str = Field(min_length=16, max_length=16, pattern=r"^\d{16}$") # Валидация номера карты в диапазоне 16 символов с паттерном
    name: str
    balance: Decimal   # Аналог Float, но без мелкой погрешности в результате

    class Config:   # Позволяет pydantic классу читать sqlalchemy элементы
        from_attributes = True

class OperationRequest(BaseModel):  # Класс для валидации интервала прибавленной суммы amount в функции receive_money
    amount: Decimal = Field(default=None, gt=0, le=100_000)
    description: str | None = None
    date: datetime



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

    return WalletResponse(
        status=f"wallet '{create.name}' created",
        wallet_id=new_wallet_id,
        wallet_number= new_wallet_number,
        name= create.name,
        balance=create.balance
    )

@router.get("/all_wallets")
def check_wallets(db: Session = Depends(get_db)):
    wallets_from_db = db.scalars(select(WalletsORM)).all()
    return wallets_from_db

@router.get("/{wallet_number}/balance", response_model=WalletResponse)
def check_balance(wallet_number: str, db: Session = Depends(get_db)):
    statement = (   # Синтаксический сахар
        select(WalletsORM)
        .where(WalletsORM.wallet_number==wallet_number)
    )

    wallet = db.scalars(statement).one_or_none()
    if wallet is None:
        raise HTTPException(404, f"Wallet '{wallet_number}' not found")
    return WalletResponse(
        status=None,
        wallet_id=wallet.id,
        wallet_number=wallet_number,
        name= wallet.name,
        balance=wallet.balance
    )

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
    db.commit()

    return {
            "status": f"Credited {request.amount}",
            "wallet_id": wallet.id,
            "amount": request.amount,
            "description": request.description,
            "Total amount": wallet.balance,
            "date": request.date.isoformat(),
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
    if wallet.balance <= request.amount:
        raise HTTPException(400, f"Insufficient funds")
    wallet.balance -= request.amount
    db.commit()

    return {
        "status": f"Credited {request.amount}",
        "wallet_id": wallet.id,
        "amount": request.amount,
        "description": request.description,
        "Total amount": wallet.balance,
        "date": request.date.isoformat(),
    }