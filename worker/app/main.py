import logging
import time

from app.database import SessionLocal
from app.worker import get_settings, process_once


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    bancs_mock_url, poll_interval, timeout_seconds = get_settings()

    logger.info("Worker iniciado | bancs_url=%s", bancs_mock_url)

    while True:
        processed_event = process_once(
            SessionLocal,
            bancs_mock_url,
            timeout_seconds
        )

        if not processed_event:
            time.sleep(poll_interval)


if __name__ == "__main__":
    main()