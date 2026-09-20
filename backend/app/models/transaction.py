# Este archivo define el modelo de datos para la tabla "transactions" en la base de datos,
# que representa las transacciones realizadas entre cuentas de clientes en el sistema.
import uuid

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False
    )

    source_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id"),
        nullable=False
    )

    destination_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id"),
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="PENDING",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    __table_args__ = (
        CheckConstraint(
            "source_account_id <> destination_account_id",
            name="chk_transactions_different_accounts"
        ),
        CheckConstraint(
            "amount > 0",
            name="chk_transactions_amount"
        ),
        CheckConstraint(
            "currency = 'USD'",
            name="chk_transactions_currency"
        ),
        CheckConstraint(
            "status IN ('PENDING', 'COMPLETED', 'FAILED')",
            name="chk_transactions_status"
        ),
    )
