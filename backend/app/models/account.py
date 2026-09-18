import uuid

from datetime import datetime

from sqlalchemy import CheckConstraint, String, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class Account(Base):

    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    account_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )

    customer_ref: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    balance: Mapped[float] = mapped_column(
        Numeric(18, 2),
        default=0,
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="USD",
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="ACTIVE",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "balance >= 0",
            name="chk_accounts_balance"
        ),
        CheckConstraint(
            "currency = 'USD'",
            name="chk_accounts_currency"
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'BLOCKED', 'CLOSED')",
            name="chk_accounts_status"
        ),
    )