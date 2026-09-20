import concurrent.futures
import requests
import uuid

URL = "http://localhost:8000/transactions"

SOURCE = "bd758d82-5e17-45fd-8320-7fe01c5f13a9"
DESTINATION = "64254a54-4903-495a-ad16-fad9a62b1239"


def make_transfer(number):
    headers = {
        "Idempotency-Key": f"concurrency-test-{uuid.uuid4()}"
    }

    payload = {
        "source_account_id": SOURCE,
        "destination_account_id": DESTINATION,
        "amount": 10
    }

    response = requests.post(
        URL,
        json=payload,
        headers=headers,
        timeout=10
    )

    return number, response.status_code, response.json()


with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(
        executor.map(make_transfer, range(1, 11))
    )


for number, status_code, data in results:
    print(
        f"Transferencia {number}: "
        f"HTTP {status_code} - "
        f"status={data.get('status')}"
    )