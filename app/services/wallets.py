import uuid
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.utils.luhn import generate_luhn_number
from app.database.connection import WalletsORM, TransactionsHistoryORM
from app.schemas.wallets import WalletCreateRequest, OperationRequest

class WalletService:
    @staticmethod
    def create_wallet(create: WalletCreateRequest, db: Session):
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

    def check_wallets(db: Session):
        wallets_from_db = db.scalars(select(WalletsORM)).all()
        return wallets_from_db

    def check_balance(wallet_number: str, db: Session):
        statement = (  # Синтаксический сахар
            select(WalletsORM)
            .where(WalletsORM.wallet_number == wallet_number)
        )

        wallet = db.scalars(statement).one_or_none()
        if wallet is None:
            raise HTTPException(404, f"Wallet '{wallet_number}' not found")
        return wallet.balance

    def add_income(wallet_number: str, request: OperationRequest, db: Session):
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
            "wallet_id": str(wallet.id),
            "amount": request.amount,
            "description": request.description,
            "Total amount": wallet.balance,
            "date": transaction_log.date.isoformat(),
        }

    def add_expense(wallet_number: str, request: OperationRequest, db: Session):
        statement = (  # Синтаксический сахар
            select(WalletsORM)
            .where(WalletsORM.wallet_number == wallet_number)
            .with_for_update()
        )

        wallet = db.scalars(statement).one_or_none()
        if wallet is None:
            raise HTTPException(404, f"Wallet '{wallet_number}' not found")

        if wallet.balance < request.amount:
            raise HTTPException(400, f"Insufficient funds for this operation")

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
            "wallet_id": str(wallet.id),
            "amount": request.amount,
            "description": request.description,
            "Total amount": wallet.balance,
            "date": transaction_log.date.isoformat(),
        }