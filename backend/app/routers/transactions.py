from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.account import Account
from backend.app.models.transaction import Transaction
from backend.app.schemas.transaction import TransactionCreate


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
    accounts_by_id = {account.id: account for account in accounts}

    source_account = accounts_by_id.get(transaction_data.source_account_id)
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

    if source_account.status != "ACTIVE" or destination_account.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Both accounts must be active"
        )

    if source_account.currency != "USD" or destination_account.currency != "USD":
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
        db.commit()
        db.refresh(transaction)
    except IntegrityError:
        db.rollback()

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

        raise HTTPException(
            status_code=500,
            detail="Unable to complete transaction"
        )

    return transaction
