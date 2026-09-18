from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.account import Account
from backend.app.schemas.account import AccountCreate, AccountResponse


router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)


@router.get("/", response_model=list[AccountResponse])
def get_accounts(db: Session = Depends(get_db)):
    return db.query(Account).all()


@router.post("/", response_model=AccountResponse, status_code=201)
def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db)
):
    account = Account(
        account_number=account_data.account_number,
        customer_ref=account_data.customer_ref
    )

    try:
        db.add(account)
        db.commit()
        db.refresh(account)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Account number already exists"
        )

    return account