from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:5432/postgres"
engine = create_engine(DATABASE_URL)
session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class WalletsORM(Base):
    __tablename__ = "all_wallets"
