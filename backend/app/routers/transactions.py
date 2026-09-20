# Este archivo define las rutas de la API relacionadas con las transacciones entre cuentas de clientes,
# incluyendo la creación de nuevas transacciones y la verificación de idempotencia.
import logging

from fastapi import APIRouter, Depends, Header, HTTPException

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.account import Account
from backend.app.models.ai_recommendation import AIRecommendation
from backend.app.models.outbox_event import OutboxEvent
from backend.app.models.transaction import Transaction
from backend.app.schemas.transaction import TransactionCreate


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@router.post("/")
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    idempotency_key: str = Header(..., alias="Idempotency-Key")
):

    if not idempotency_key.strip() or len(idempotency_key) > 64:
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key must be between 1 and 64 characters"
        )

    existing_transaction = db.execute(
        select(Transaction).where(
            Transaction.idempotency_key == idempotency_key
        )
    ).scalar_one_or_none()

    if existing_transaction is not None:
        logger.info(
            "Transacción existente | transaction_id=%s | idempotency_key=%s",
            existing_transaction.id,
            idempotency_key
        )
        return existing_transaction

    account_ids = sorted([
        transaction_data.source_account_id,
        transaction_data.destination_account_id
    ])

    accounts = db.execute(
        select(Account)
        .where(Account.id.in_(account_ids))
        .order_by(Account.id)
        .with_for_update()
    ).scalars().all()

    accounts_by_id = {
        account.id: account
        for account in accounts
    }

    source_account = accounts_by_id.get(
        transaction_data.source_account_id
    )

    destination_account = accounts_by_id.get(
        transaction_data.destination_account_id
    )

    if source_account is None or destination_account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    if source_account.id == destination_account.id:
        raise HTTPException(
            status_code=400,
            detail="Source and destination accounts must be different"
        )

    if (
        source_account.status != "ACTIVE"
        or destination_account.status != "ACTIVE"
    ):
        raise HTTPException(
            status_code=400,
            detail="Both accounts must be active"
        )

    if (
        source_account.currency != "USD"
        or destination_account.currency != "USD"
    ):
        raise HTTPException(
            status_code=400,
            detail="Both accounts must use USD"
        )

    if source_account.balance < transaction_data.amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    source_account.balance -= transaction_data.amount
    destination_account.balance += transaction_data.amount

    transaction = Transaction(
        idempotency_key=idempotency_key,
        source_account_id=source_account.id,
        destination_account_id=destination_account.id,
        amount=transaction_data.amount,
        currency="USD",
        status="COMPLETED"
    )

    try:
        db.add(transaction)
        db.flush()

        logger.info(
            "Transferencia creada | transaction_id=%s | amount=%s",
            transaction.id,
            transaction.amount
        )

        # Evento para el Worker de Bancs
        outbox_event = OutboxEvent(
            transaction_id=transaction.id,
            event_type="TRANSFER_CREATED",
            payload={
                "transaction_id": str(transaction.id),
                "source_account_id": str(source_account.id),
                "destination_account_id": str(destination_account.id),
                "amount": float(transaction_data.amount),
                "currency": "USD"
            },
            status="PENDING",
            attempts=0
        )

        db.add(outbox_event)

        logger.info(
            "Outbox creado | transaction_id=%s | event_type=%s",
            transaction.id,
            outbox_event.event_type
        )

        # Trabajo asíncrono para el AI Worker
        ai_recommendation = AIRecommendation(
            account_id=source_account.id,
            recommendation=None,
            model="gemini-3.6-flash",
            status="PENDING"
        )

        db.add(ai_recommendation)

        # Una sola transacción para:
        # 1. Transferencia
        # 2. Outbox
        # 3. Trabajo de IA
        db.commit()
        db.refresh(transaction)

        logger.info(
            "Transferencia completada | transaction_id=%s",
            transaction.id
        )

    except IntegrityError:
        db.rollback()

        logger.exception(
            "Error de integridad | idempotency_key=%s",
            idempotency_key
        )

        existing_transaction = db.execute(
            select(Transaction).where(
                Transaction.idempotency_key == idempotency_key
            )
        ).scalar_one_or_none()

        if existing_transaction is not None:
            return existing_transaction

        raise HTTPException(
            status_code=500,
            detail="Unable to complete transaction"
        )

    except SQLAlchemyError:
        db.rollback()

        logger.exception(
            "Error de base de datos | idempotency_key=%s",
            idempotency_key
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to complete transaction"
        )

    return transaction

