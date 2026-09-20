from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    source_account_id: UUID
    destination_account_id: UUID
    amount: Decimal = Field(gt=0)
