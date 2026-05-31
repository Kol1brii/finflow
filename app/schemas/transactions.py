import uuid
from decimal import Decimal
from pydantic import BaseModel, Field

class TransferResponse(BaseModel):
    from_wallet_id: uuid.UUID
    to_wallet_id: uuid.UUID
    from_wallet_number: str
    to_wallet_number: str
    amount: Decimal = Field(gt=0, le=100_000)
    description: str | None = None

class TransferRequest(BaseModel):
    from_wallet_number: str
    to_wallet_number: str
    amount: Decimal = Field(gt=0, le=100_000)
    description: str | None = None