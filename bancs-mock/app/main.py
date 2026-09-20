import logging
import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse

from app.schemas import BankTransactionRequest, BankTransactionResponse


logger = logging.getLogger(__name__)


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
    logger.info(
        "Transacción recibida | transaction_id=%s",
        transaction.transaction_id
    )

    forced_error = os.getenv("MOCK_ERROR")

    if forced_error is not None and forced_error != "":
        mock_error = forced_error

    if mock_error is not None:
        try:
            error_code = int(mock_error)
        except ValueError:
            logger.warning(
                "Header X-Mock-Error inválido | transaction_id=%s",
                transaction.transaction_id
            )

            raise HTTPException(
                status_code=400,
                detail="X-Mock-Error must be 400, 500, or 503"
            )

        if error_code not in MOCK_ERROR_MESSAGES:
            logger.warning(
                "Código de error no permitido | transaction_id=%s | status=%s",
                transaction.transaction_id,
                error_code
            )

            raise HTTPException(
                status_code=400,
                detail="X-Mock-Error must be 400, 500, or 503"
            )

        logger.warning(
            "Bancs Mock simulando error | transaction_id=%s | status=%s",
            transaction.transaction_id,
            error_code
        )

        return JSONResponse(
            status_code=error_code,
            content={
                "transaction_id": str(transaction.transaction_id),
                "status": "FAILED",
                "error": MOCK_ERROR_MESSAGES[error_code]
            }
        )

    logger.info(
        "Transacción procesada correctamente | transaction_id=%s",
        transaction.transaction_id
    )

    return BankTransactionResponse(
        transaction_id=transaction.transaction_id,
        status="PROCESSED",
        message="Bank transaction processed successfully"
    )

