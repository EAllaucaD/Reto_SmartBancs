import time
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env")


from app.database import SessionLocal
from app.worker import process_one_job


def main():
    print("AI Worker iniciado")

    while True:
        db = SessionLocal()

        try:
            processed = process_one_job(db)
        finally:
            db.close()

        if not processed:
            time.sleep(5)


if __name__ == "__main__":
    main()