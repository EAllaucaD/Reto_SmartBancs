import time
from pathlib import Path

from dotenv import load_dotenv

# Se encarga de cargar las variables de entorno desde un archivo .env ubicado en el directorio raíz del proyecto.
ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env")


from app.database import SessionLocal
from app.worker import process_one_job

# El archivo principal del worker de AI. Se encarga de iniciar el proceso de escucha y procesamiento 
# de trabajos pendientes en la base de datos.
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