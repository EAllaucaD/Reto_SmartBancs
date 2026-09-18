from fastapi import FastAPI
from sqlalchemy import text
# Se encarga de importar la clase engine desde el módulo database para establecer la conexión con la base de datos.
from backend.app.database import engine

# Se encarga de importar la clase Account desde el módulo account para poder interactuar con la tabla "accounts" en la base de datos.
from backend.app.models.account import Account

# Se encarga de importar el router de cuentas desde el módulo accounts para poder manejar las rutas relacionadas con las cuentas.
from backend.app.routers.accounts import router as accounts_router
from backend.app.routers.transactions import router as transactions_router


app = FastAPI(
    title="SmartBancs API",
    version="0.1.0"
)

#Se encarga de incluir el router de cuentas en la aplicación FastAPI para que las rutas relacionadas con las cuentas estén disponibles en la API.
app.include_router(accounts_router)
app.include_router(transactions_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected"
    }