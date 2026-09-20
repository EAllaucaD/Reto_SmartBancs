# Este archivo configura la conexión a la base de datos utilizando 
# SQLAlchemy y define la clase base para los modelos de datos.

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


load_dotenv()


DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"localhost:5432/"
    f"{os.getenv('POSTGRES_DB')}"
)

# Conexión a la base de datos. Se utiliza para ejecutar consultas SQL y obtener resultados.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

# Sesiones de la base de datos. Se utiliza para interactuar con la base de datos.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()



# La base de todos nuestro modelos de SQLAlchemy. Todos los modelos deben heredar de esta clase.
class Base(DeclarativeBase):
    pass