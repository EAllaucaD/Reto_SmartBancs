from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import httpx
from sqlalchemy.dialects import postgresql

from app.worker import (
    MAX_ATTEMPTS,
    claim_pending_event,
    mark_failed,
    mark_processed,
    process_event,
)


class FakeDatabase:

    def __init__(self, event):
        self.event = event

    def get(self, model, event_id):
        return self.event if self.event.id == event_id else None

    def commit(self):
        return None


class FakeExecuteResult:

    def __init__(self, event):
        self.event = event

    def scalar_one_or_none(self):
        return self.event

    def scalars(self):
        return self

    def all(self):
        return [] if self.event is None else [self.event]


class ClaimDatabase:

    def __init__(self, event):
        self.event = event
        self.statement = None
        self.commits = 0
        self.rollbacks = 0

    def execute(self, statement):
        self.statement = statement
        return FakeExecuteResult(self.event)

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def make_event(attempts=0):
    return SimpleNamespace(
        id=uuid4(),
        status="PROCESSING",
        attempts=attempts,
        next_attempt_at=datetime.now(timezone.utc),
        last_error=None,
        processed_at=None,
        payload={
            "transaction_id": str(uuid4()),
            "source_account_id": str(uuid4()),
            "destination_account_id": str(uuid4()),
            "amount": 100.0,
            "currency": "USD"
        }
    )


def make_response(status_code):
    request = httpx.Request("POST", "http://bancs-mock:8000/bank-transactions")
    return httpx.Response(status_code, request=request)


def test_claim_pending_event_uses_skip_locked():
    event = make_event()
    event.status = "PENDING"
    db = ClaimDatabase(event)

    claimed_event = claim_pending_event(db)
    compiled = str(
        db.statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        )
    )

    assert claimed_event is event
    assert event.status == "PROCESSING"
    assert db.commits == 1
    assert "FOR UPDATE SKIP LOCKED" in compiled


def test_claim_pending_event_returns_none_when_unavailable():
    db = ClaimDatabase(None)

    assert claim_pending_event(db) is None
    assert db.rollbacks == 1


def test_second_worker_skips_event_claimed_by_first_worker():
    event = make_event()
    event.status = "PENDING"
    first_worker_db = ClaimDatabase(event)
    second_worker_db = ClaimDatabase(None)

    assert claim_pending_event(first_worker_db) is event
    assert claim_pending_event(second_worker_db) is None
    assert event.status == "PROCESSING"


def test_claim_query_requires_event_to_be_available_now():
    event = make_event()
    event.status = "PENDING"
    db = ClaimDatabase(event)

    claim_pending_event(db)
    compiled = str(
        db.statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        )
    )

    assert "next_attempt_at <= now()" in compiled


def test_success_marks_event_processed():
    event = make_event()
    db = FakeDatabase(event)
    client = Mock()
    client.post.return_value = make_response(200)

    process_event(db, event, client, "http://bancs-mock:8000")

    assert event.attempts == 1
    assert event.status == "PROCESSED"
    assert event.last_error is None
    assert event.processed_at is not None


def test_http_500_schedules_retry():
    event = make_event()
    db = FakeDatabase(event)
    client = Mock()
    client.post.return_value = make_response(500)

    process_event(db, event, client, "http://bancs-mock:8000")

    assert event.attempts == 1
    assert event.status == "PENDING"
    assert event.next_attempt_at > datetime.now(timezone.utc)
    assert event.last_error == "Bancs Mock returned HTTP 500"


def test_http_503_schedules_retry():
    event = make_event()
    db = FakeDatabase(event)
    client = Mock()
    client.post.return_value = make_response(503)

    process_event(db, event, client, "http://bancs-mock:8000")

    assert event.status == "PENDING"
    assert event.attempts == 1


def test_timeout_schedules_retry():
    event = make_event()
    db = FakeDatabase(event)
    client = Mock()
    client.post.side_effect = httpx.ReadTimeout("timeout")

    process_event(db, event, client, "http://bancs-mock:8000")

    assert event.status == "PENDING"
    assert event.attempts == 1
    assert event.last_error == "timeout"


def test_third_failure_marks_event_failed():
    event = make_event(attempts=2)
    db = FakeDatabase(event)
    client = Mock()
    client.post.return_value = make_response(500)

    process_event(db, event, client, "http://bancs-mock:8000")

    assert event.attempts == MAX_ATTEMPTS
    assert event.status == "FAILED"


def test_http_400_fails_without_retry():
    event = make_event()
    db = FakeDatabase(event)
    client = Mock()
    client.post.return_value = make_response(400)

    process_event(db, event, client, "http://bancs-mock:8000")

    assert event.attempts == 1
    assert event.status == "FAILED"
    assert event.last_error == "Bancs Mock returned HTTP 400"


def test_mark_processed_clears_error():
    event = make_event()
    event.last_error = "previous error"

    mark_processed(FakeDatabase(event), event.id)

    assert event.status == "PROCESSED"
    assert event.last_error is None


def test_mark_failed_without_retry_keeps_failed_state():
    event = make_event()

    mark_failed(FakeDatabase(event), event.id, "bad request", retry=False)

    assert event.status == "FAILED"
    assert event.last_error == "bad request"
