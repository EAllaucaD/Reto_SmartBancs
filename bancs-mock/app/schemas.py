# Este archivo define los esquemas de datos para las solicitudes y 
# respuestas de transacciones bancarias en la API mock de Bancs.

from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class BankTransactionRequest(BaseModel):
    transaction_id: UUID
    source_account_id: UUID
    destination_account_id: UUID
    amount: Decimal = Field(gt=0)
    currency: Literal["USD"]


class BankTransactionResponse(BaseModel):
    transaction_id: UUID
    status: str
    message: str
