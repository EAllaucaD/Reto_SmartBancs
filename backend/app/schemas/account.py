from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    account_number: str = Field(min_length=1, max_length=20)
    customer_ref: str = Field(min_length=1, max_length=50)
    

# El cliente solo puede enviar esos valores

class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_number: str
    customer_ref: str
    balance: Decimal
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime
    
# Dos esquemas diferentes para la creación de cuentas y la respuesta de cuentas. 
# Esto permite que el cliente solo pueda enviar ciertos valores al crear una cuenta, mientras que la respuesta 
# de la cuenta incluye todos los campos de la cuenta, incluyendo los generados automáticamente por la base de datos.