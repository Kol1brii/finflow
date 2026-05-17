from datetime import datetime
from os import name

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, condecimal
from decimal import Decimal
from app.utils.luhn import generate_luhn_number, validate_luhn
import uuid



router = APIRouter(prefix="/wallets", tags=["wallets"])

ALL_WALLETS = {}  # Все кошельки
CARD_INDEX = {}   # Обращение к UUID карты по её номеру
TRANSACTION_HISTORY = []   # История транзакций

class WalletCreateRequest(BaseModel):
    name: str
    balance: Decimal | None = 0

class WalletResponse(BaseModel):  # Pydantic класс
    status: str | None = None
    wallet_number: str = Field(min_length=16, max_length=16, pattern=r"^\d{16}$") # Валидация номера карты в диапазоне 16 символов с паттерном
    wallet_id: str
    name: str
    balance: Decimal # Аналог Float но без мелкой погрешности в результате

class OperationRequest(BaseModel):  # Класс для валидации интервала прибавленной суммы amount в функции receive_money
    amount: Decimal = Field(default=None, gt=0, le=100_000)
    description: str | None = None
    date: datetime

@router.post("/create_wallet", response_model=WalletResponse, status_code=201)
def create_wallet(create: WalletCreateRequest):
    new_wallet_id = str(uuid.uuid4())
    new_wallet_number = generate_luhn_number(16)
    ALL_WALLETS[new_wallet_id] = {
        "wallet_number": new_wallet_number,
        "name": create.name,
        "balance": create.balance
    }
    CARD_INDEX[new_wallet_number] = new_wallet_id

    return {
        "status": f"wallet '{create.name}' created",
        "wallet_number": new_wallet_number,
        "wallet_id": new_wallet_id,
        "name": create.name,
        "balance": create.balance
    }

@router.get("/all_wallets")
def check_wallets():
    return ALL_WALLETS

@router.get("/{wallet_number}/balance", response_model=WalletResponse)
def check_balance(wallet_number: str):
    wallet_id = CARD_INDEX[wallet_number]
    if not wallet_id:
        raise HTTPException(404, f"Wallet '{wallet_number}' not found")
    if wallet_id not in ALL_WALLETS:
        raise HTTPException(404, f"Wallet '{wallet_id}' not found")
    return {
        "wallet_id": wallet_id,
        "name": ALL_WALLETS[wallet_id]["name"],
        "balance": ALL_WALLETS[wallet_id]["balance"]
    }

@router.post("/{wallet_number}/income")
def add_income(wallet_number: str, request: OperationRequest):
    wallet_id = CARD_INDEX[wallet_number]
    if not wallet_id:
        raise HTTPException(404, f"Wallet '{wallet_number}' not found")
    if wallet_id not in ALL_WALLETS:
        raise HTTPException(404, f"Wallet {wallet_id} not found")
    ALL_WALLETS[wallet_id]["balance"] += request.amount

    TRANSACTION_HISTORY.append(
        {
            "status": f"Credited {request.amount}",
            "wallet_id": wallet_id,
            "name": ALL_WALLETS[wallet_id]["name"],
            "amount": request.amount,
            "description": request.description,
            "Total amount": ALL_WALLETS[wallet_id]["balance"],
            "date": request.date.isoformat(),
        }
    )
    return {
            "status": f"Credited {request.amount}",
            "wallet_id": wallet_id,
            "name": ALL_WALLETS[wallet_id]["name"],
            "amount": request.amount,
            "description": request.description,
            "Total amount": ALL_WALLETS[wallet_id]["balance"],
            "date": request.date.isoformat(),
        }


@router.post("/{wallet_number}/expense")
def add_expense(wallet_number: str, request: OperationRequest):
    wallet_id = CARD_INDEX[wallet_number]
    if not wallet_id:
        raise HTTPException(404, f"Wallet '{wallet_number}' not found")
    if wallet_id not in ALL_WALLETS:
        raise HTTPException(404, f"Wallet {wallet_id} not found")
    elif ALL_WALLETS[wallet_id]["balance"] < request.amount:
        raise HTTPException(400, "Not enough money")
    ALL_WALLETS[wallet_id]["balance"] -= request.amount

    TRANSACTION_HISTORY.append(
        {
            "status": f"deducted {request.amount}",
            "wallet_id": wallet_id,
            "name": ALL_WALLETS[wallet_id]["name"],
            "amount": request.amount,
            "description": request.description,
            "Total amount": ALL_WALLETS[wallet_id]["balance"],
            "date": request.date.isoformat(),
        }
    )
    return {
        "status": f"deducted {request.amount} to wallet",
        "wallet_id": wallet_id,
        "name": ALL_WALLETS[wallet_id]["name"],
        "amount": request.amount,
        "description": request.description,
        "Total amount": ALL_WALLETS[wallet_id]["balance"],
        "date": request.date.isoformat(),
    }
