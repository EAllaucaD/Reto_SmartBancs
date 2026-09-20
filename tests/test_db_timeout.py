import os
import threading
import time

import psycopg
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}


def get_connection(application_name: str):
    return psycopg.connect(
        **DB_CONFIG,
        application_name=application_name,
    )


def get_account_id():
    with get_connection("db-timeout-setup") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM accounts LIMIT 1")
            result = cur.fetchone()

            if not result:
                raise RuntimeError(
                    "No existe ninguna cuenta en la tabla accounts. "
                    "Crea al menos una cuenta antes de ejecutar la prueba."
                )

            return result[0]


def blocker(account_id, ready_event, release_event):
    with get_connection("db-timeout-blocker") as conn:
        with conn.cursor() as cur:
            cur.execute("BEGIN")

            cur.execute(
                """
                SELECT id
                FROM accounts
                WHERE id = %s
                FOR UPDATE
                """,
                (account_id,),
            )

            print(f"[A] Fila bloqueada: {account_id}")
            print(f"[A] PID PostgreSQL: {conn.info.backend_pid}")

            ready_event.set()

            print("[A] Manteniendo el bloqueo durante 8 segundos...")
            release_event.wait(timeout=8)

            cur.execute("ROLLBACK")

            print("[A] Bloqueo liberado.")


def waiter(account_id, ready_event):
    ready_event.wait()

    time.sleep(0.5)

    try:
        with get_connection("db-timeout-waiter") as conn:
            with conn.cursor() as cur:
                cur.execute("SET statement_timeout = '3000ms'")

                print(f"[B] Intentando modificar la fila: {account_id}")
                print(f"[B] PID PostgreSQL: {conn.info.backend_pid}")
                print("[B] Timeout configurado: 3000 ms")

                cur.execute(
                    """
                    UPDATE accounts
                    SET updated_at = NOW()
                    WHERE id = %s
                    """,
                    (account_id,),
                )

                conn.commit()

                print("[B] La operación terminó correctamente.")

    except psycopg.errors.QueryCanceled:
        print("[B] TIMEOUT DETECTADO")
        print("[B] PostgreSQL canceló la consulta por statement_timeout.")


def inspect_database(waiter_ready_event):
    waiter_ready_event.wait()

    time.sleep(1)

    with get_connection("db-timeout-observer") as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    pid,
                    application_name,
                    state,
                    wait_event_type,
                    wait_event,
                    query
                FROM pg_stat_activity
                WHERE application_name IN (
                    'db-timeout-blocker',
                    'db-timeout-waiter'
                )
                ORDER BY pid
                """
            )

            rows = cur.fetchall()

            print("\n[OBSERVADOR] pg_stat_activity:")

            for row in rows:
                print(
                    f"PID={row[0]} | "
                    f"APP={row[1]} | "
                    f"STATE={row[2]} | "
                    f"WAIT_TYPE={row[3]} | "
                    f"WAIT_EVENT={row[4]}"
                )
                print(f"QUERY={row[5]}\n")

            cur.execute(
                """
                SELECT
                    pid,
                    pg_blocking_pids(pid) AS blocking_pids
                FROM pg_stat_activity
                WHERE application_name = 'db-timeout-waiter'
                """
            )

            blocking = cur.fetchone()

            if blocking:
                print(
                    "[OBSERVADOR] Proceso bloqueante identificado: "
                    f"PID {blocking[1]}"
                )


def main():
    account_id = get_account_id()

    print("=" * 60)
    print("PRUEBA CONTROLADA: DB TIMEOUT")
    print("=" * 60)
    print(f"Cuenta utilizada: {account_id}\n")

    blocker_ready = threading.Event()
    waiter_ready = threading.Event()

    release_blocker = threading.Event()

    blocker_thread = threading.Thread(
        target=blocker,
        args=(account_id, blocker_ready, release_blocker),
    )

    waiter_thread = threading.Thread(
        target=waiter,
        args=(account_id, blocker_ready),
    )

    observer_thread = threading.Thread(
        target=inspect_database,
        args=(waiter_ready,),
    )

    blocker_thread.start()
    blocker_ready.wait()

    waiter_thread.start()

    time.sleep(0.5)

    waiter_ready.set()
    observer_thread.start()

    waiter_thread.join()

    release_blocker.set()

    blocker_thread.join()
    observer_thread.join()

    print("\n" + "=" * 60)
    print("PRUEBA FINALIZADA")
    print("=" * 60)


if __name__ == "__main__":
    main()