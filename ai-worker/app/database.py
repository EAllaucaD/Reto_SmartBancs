import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Se encarga de crear la conexión a la base de datos y proporcionar una sesión para interactuar con ella. 
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://smartbancs:change_me@localhost:5432/smartbancs"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)