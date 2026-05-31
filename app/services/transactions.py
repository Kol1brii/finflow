from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database.connection import TransactionsHistoryORM

class WalletService:
    @staticmethod
    def check_transactions(db: Session):
        transactions = db.scalars(select(TransactionsHistoryORM)).all()
        return transactions