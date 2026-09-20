from locust import HttpUser, task, between
import uuid
import random


ACCOUNT_IDS = [
    "0c897567-00b4-40e7-bba2-0be2c5a62180",
    "92a7cfc1-8298-4ce7-8f11-6a4d1b4aac6b",
    "cc2aa910-25c8-4022-860a-7805b8912dc5",
    "269a5d1c-d74d-42e8-9ad5-5bfe95812f06",
    "4176ebf4-d8e8-4f54-a355-6884be35aef6",
]


class SmartBancsUser(HttpUser):
    wait_time = between(0.001, 0.005)

    @task
    def transfer(self):
        source, destination = random.sample(ACCOUNT_IDS, 2)

        with self.client.post(
            "/transactions/",
            json={
                "source_account_id": source,
                "destination_account_id": destination,
                "amount": 1
            },
            headers={
                "Idempotency-Key": f"load-{uuid.uuid4()}"
            },
            name="/transactions",
            catch_response=True
        ) as response:

            if response.status_code != 200:
                print(
                    f"ERROR {response.status_code}: "
                    f"{response.text}"
                )
                response.failure(
                    f"HTTP {response.status_code}"
                )