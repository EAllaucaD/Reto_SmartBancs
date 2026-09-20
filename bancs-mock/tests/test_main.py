#Este archivo contiene pruebas unitarias para la aplicación FastAPI que simula un servicio bancario.    
# Hace uso de TestClient para enviar solicitudes HTTP a la API y verificar las respuestas,
# incluyendo casos de éxito, errores de validación y errores simulados del banco.

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

VALID_TRANSACTION = {
    "transaction_id": "55b53a76-cc31-4fa6-b749-3633b5afd521",
    "source_account_id": "bd758d82-5e17-45fd-8320-7fe01c5f13a9",
    "destination_account_id": "64254a54-4903-495a-ad16-fad9a62b1239",
    "amount": 100.00,
    "currency": "USD"
}


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_valid_bank_transaction():
    response = client.post("/bank-transactions", json=VALID_TRANSACTION)

    assert response.status_code == 200
    assert response.json() == {
        "transaction_id": VALID_TRANSACTION["transaction_id"],
        "status": "PROCESSED",
        "message": "Bank transaction processed successfully"
    }


def test_invalid_transaction_data():
    invalid_transaction = {
        **VALID_TRANSACTION,
        "amount": 0
    }

    response = client.post("/bank-transactions", json=invalid_transaction)

    assert response.status_code == 422


def test_simulated_400_error():
    response = client.post(
        "/bank-transactions",
        json=VALID_TRANSACTION,
        headers={"X-Mock-Error": "400"}
    )

    assert response.status_code == 400
    assert response.json() == {
        "transaction_id": VALID_TRANSACTION["transaction_id"],
        "status": "FAILED",
        "error": "Simulated bank bad request"
    }


def test_simulated_500_error():
    response = client.post(
        "/bank-transactions",
        json=VALID_TRANSACTION,
        headers={"X-Mock-Error": "500"}
    )

    assert response.status_code == 500
    assert response.json() == {
        "transaction_id": VALID_TRANSACTION["transaction_id"],
        "status": "FAILED",
        "error": "Simulated bank internal error"
    }


def test_simulated_503_error():
    response = client.post(
        "/bank-transactions",
        json=VALID_TRANSACTION,
        headers={"X-Mock-Error": "503"}
    )

    assert response.status_code == 503
    assert response.json() == {
        "transaction_id": VALID_TRANSACTION["transaction_id"],
        "status": "FAILED",
        "error": "Simulated bank service unavailable"
    }
