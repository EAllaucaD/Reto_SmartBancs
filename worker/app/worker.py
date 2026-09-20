import os

from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import httpx

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import OutboxEvent


MAX_ATTEMPTS = 3
RECOVERABLE_STATUS_CODES = {500, 502, 503, 504}


def claim_pending_event(db: Session) -> OutboxEvent | None:
    event = db.execute(
        select(OutboxEvent)
        .where(
            OutboxEvent.status == "PENDING",
            OutboxEvent.next_attempt_at <= func.now()
        )
        .order_by(OutboxEvent.created_at)
        .with_for_update(skip_locked=True)
        .limit(1)
    ).scalar_one_or_none()

    if event is None:
        db.rollback()
        return None

    event.status = "PROCESSING"
    db.commit()
    return event


def mark_processed(db: Session, event_id: Any) -> None:
    event = db.get(OutboxEvent, event_id)
    if event is None:
        return

    event.status = "PROCESSED"
    event.processed_at = datetime.now(timezone.utc)
    event.last_error = None
    db.commit()


def mark_failed(
    db: Session,
    event_id: Any,
    error_message: str,
    retry: bool
) -> None:
    event = db.get(OutboxEvent, event_id)
    if event is None:
        return

    if retry and event.attempts < MAX_ATTEMPTS:
        event.status = "PENDING"
        event.next_attempt_at = datetime.now(timezone.utc) + timedelta(
            seconds=2 ** event.attempts
        )
    else:
        event.status = "FAILED"

    event.last_error = error_message
    db.commit()


def increment_attempt(db: Session, event_id: Any) -> int | None:
    event = db.get(OutboxEvent, event_id)
    if event is None:
        return None

    event.attempts += 1
    db.commit()
    return event.attempts


def build_request_payload(event: OutboxEvent) -> dict[str, Any]:
    return event.payload


def process_event(
    db: Session,
    event: OutboxEvent,
    client: httpx.Client,
    bancs_mock_url: str
) -> None:
    attempts = increment_attempt(db, event.id)
    if attempts is None:
        return

    try:
        response = client.post(
            f"{bancs_mock_url}/bank-transactions",
            json=build_request_payload(event)
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        error_message = f"Bancs Mock returned HTTP {status_code}"
        retry = status_code in RECOVERABLE_STATUS_CODES or status_code >= 500
        mark_failed(
            db,
            event.id,
            error_message,
            retry=retry and attempts < MAX_ATTEMPTS
        )
        return
    except (httpx.TimeoutException, httpx.RequestError) as error:
        mark_failed(
            db,
            event.id,
            str(error) or error.__class__.__name__,
            retry=attempts < MAX_ATTEMPTS
        )
        return

    mark_processed(db, event.id)


def process_once(
    session_factory: Callable[[], Session],
    bancs_mock_url: str,
    timeout_seconds: float
) -> bool:
    db = session_factory()
    try:
        event = claim_pending_event(db)
        if event is None:
            return False

        with httpx.Client(timeout=timeout_seconds) as client:
            process_event(db, event, client, bancs_mock_url)
        return True
    finally:
        db.close()


def get_settings() -> tuple[str, float, float]:
    return (
        os.getenv("BANCS_MOCK_URL", "http://bancs-mock:8000").rstrip("/"),
        float(os.getenv("POLL_INTERVAL_SECONDS", "5")),
        float(os.getenv("HTTP_TIMEOUT_SECONDS", "5"))
    )
