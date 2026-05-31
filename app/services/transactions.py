from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database.connection import TransactionsHistoryORM, WalletsORM
from decimal import Decimal
from fastapi import HTTPException
import uuid

class WalletService:
    @staticmethod
    def check_transactions(db: Session):
        transactions = db.scalars(select(TransactionsHistoryORM)).all()
        return transactions

    @staticmethod
    def transfer(from_wallet_number: str, to_wallet_number: str, amount: Decimal, description: str, db: Session):
        from_statement = (
            select(WalletsORM)
            .where(WalletsORM.wallet_number == from_wallet_number)
            .with_for_update()
        )

        to_statement = (
            select(WalletsORM)
            .where(WalletsORM.wallet_number==to_wallet_number)
            .with_for_update()
        )

        if from_wallet_number < to_wallet_number:   # Защита от Deadlock путём блокирования меньшего номера кошелька
            from_wallet = db.scalars(from_statement).one_or_none()
            to_wallet = db.scalars(to_statement).one_or_none()
        else:
            to_wallet = db.scalars(to_statement).one_or_none()
            from_wallet = db.scalars(from_statement).one_or_none()

        if from_wallet is None:
            raise HTTPException(404, f"Wallet '{from_wallet_number}' not found")
        elif to_wallet is None:
            raise HTTPException(404, f"Wallet '{to_wallet_number}' not found")

        if from_wallet.balance < amount:
            raise HTTPException(400, f"Insufficient funds for this operation")

        from_wallet.balance -= amount
        to_wallet.balance += amount

        from_wallet_transaction_log = TransactionsHistoryORM(
            wallet_id=from_wallet.id,
            status=f"add expense, transfer out {to_wallet_number}",
            amount=-amount,
            description=description,
            balance=from_wallet.balance
        )

        to_wallet_transaction_log = TransactionsHistoryORM(
            wallet_id=to_wallet.id,
            status=f"add income, transfer in {from_wallet_number}",
            amount=amount,
            description=description,
            balance=to_wallet.balance
        )

        db.add(from_wallet_transaction_log)
        db.add(to_wallet_transaction_log)
        db.commit()

        return {
            "from_wallet_id": from_wallet.id,
            "to_wallet_id": to_wallet.id,
            "from_wallet_number": from_wallet_number,
            "to_wallet_number": to_wallet_number,
            "amount": amount,
            "description": description,
        }