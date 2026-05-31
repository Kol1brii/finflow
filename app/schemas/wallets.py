import uuid
from decimal import Decimal
from pydantic import BaseModel, Field

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
    amount: Decimal = Field(gt=0, le=100_000)
    description: str | None = None