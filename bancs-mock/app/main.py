import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

from app.schemas import BankTransactionRequest, BankTransactionResponse


app = FastAPI(
    title="Bancs Mock",
    version="0.1.0"
)


MOCK_ERROR_MESSAGES = {
    400: "Simulated bank bad request",
    500: "Simulated bank internal error",
    503: "Simulated bank service unavailable"
}


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.post(
    "/bank-transactions",
    response_model=BankTransactionResponse
)
def process_bank_transaction(
    transaction: BankTransactionRequest,
    mock_error: str | None = Header(None, alias="X-Mock-Error")
):
    forced_error = os.getenv("MOCK_ERROR")

    if forced_error is not None and forced_error != "":
        mock_error = forced_error

    if mock_error is not None:
        try:
            error_code = int(mock_error)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="X-Mock-Error must be 400, 500, or 503"
            )

        if error_code not in MOCK_ERROR_MESSAGES:
            raise HTTPException(
                status_code=400,
                detail="X-Mock-Error must be 400, 500, or 503"
            )

        return JSONResponse(
            status_code=error_code,
            content={
                "transaction_id": str(transaction.transaction_id),
                "status": "FAILED",
                "error": MOCK_ERROR_MESSAGES[error_code]
            }
        )

    return BankTransactionResponse(
        transaction_id=transaction.transaction_id,
        status="PROCESSED",
        message="Bank transaction processed successfully"
    )