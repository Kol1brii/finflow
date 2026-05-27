import uuid, os
from decimal import Decimal
from datetime import datetime

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, DeclarativeBase, relationship
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, Numeric, DateTime, func

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:admin@127.0.0.1:5432/postgres"
)

engine = create_engine(DATABASE_URL)
session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class WalletsORM(Base):
    __tablename__ = "all_wallets"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    wallet_number: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(32))
    balance: Mapped[Decimal] = mapped_column(Numeric(scale=2), default=Decimal("0.00"))
    transactions: Mapped[list["TransactionsHistoryORM"]] = relationship(back_populates="wallet")

class TransactionsHistoryORM(Base):
    __tablename__ = "transactions_history"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    wallet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("all_wallets.id"))
    status: Mapped[str] = mapped_column(String(50))
    amount: Mapped[Decimal] = mapped_column(Numeric(scale=2))
    description: Mapped[str] = mapped_column(String(100))
    balance: Mapped[Decimal] = mapped_column(Numeric(scale=2), default=Decimal("0.00"))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    wallet: Mapped["WalletsORM"] = relationship(back_populates="transactions")

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()