import pandas as pd


RAW_FILE = "etl/data/raw/bancs_transactions_raw.csv"
CLEAN_FILE = "etl/data/processed/transactions_clean.csv"
REJECTED_FILE = "etl/data/processed/transactions_rejected.csv"


# 1. Leer datos RAW

df = pd.read_csv(RAW_FILE)

print(f"Registros RAW: {len(df)}")


# 2. Normalizar campos

df["transaction_id"] = (
    df["transaction_id"]
    .astype("string")
    .str.strip()
)

df["account_number"] = (
    pd.to_numeric(df["account_number"], errors="coerce")
    .astype("Int64")
    .astype("string")
)

df["amount"] = (
    df["amount"]
    .astype("string")
    .str.strip()
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
)

df["amount"] = pd.to_numeric(
    df["amount"],
    errors="coerce"
)

df["currency"] = (
    df["currency"]
    .astype("string")
    .str.strip()
    .str.upper()
)

df["transaction_date"] = pd.to_datetime(
    df["transaction_date"],
    errors="coerce",
    format="mixed"
)

df["status"] = (
    df["status"]
    .astype("string")
    .str.strip()
    .str.upper()
)


# 3. Validaciones individuales

valid_status = {
    "COMPLETED",
    "FAILED",
    "PENDING"
}


valid_transaction_id = (
    df["transaction_id"].notna()
    & df["transaction_id"].ne("")
    & ~df["transaction_id"].duplicated(keep=False)
)

valid_account = df["account_number"].notna()

valid_amount = (
    df["amount"].notna()
    & (df["amount"] > 0)
)

valid_currency = df["currency"].eq("USD")

valid_date = df["transaction_date"].notna()

valid_status_column = df["status"].isin(valid_status)


# 4. Determinar si cada fila es válida

valid_rows = (
    valid_transaction_id.fillna(False)
    & valid_account.fillna(False)
    & valid_amount.fillna(False)
    & valid_currency.fillna(False)
    & valid_date.fillna(False)
    & valid_status_column.fillna(False)
)


# 5. Separar datos

clean_df = df.loc[valid_rows].copy()

rejected_df = df.loc[~valid_rows].copy()


# 6. Verificación

total_processed = len(clean_df) + len(rejected_df)

if total_processed != len(df):
    print()
    print("ERROR: Algunos registros no fueron clasificados.")
    print(f"RAW:       {len(df)}")
    print(f"CLEAN:     {len(clean_df)}")
    print(f"REJECTED:  {len(rejected_df)}")
    print(f"TOTAL:     {total_processed}")
    raise ValueError("El ETL no procesó todos los registros.")


# 7. Formato final de fecha

clean_df["transaction_date"] = clean_df[
    "transaction_date"
].dt.strftime("%Y-%m-%d %H:%M:%S")

rejected_df["transaction_date"] = rejected_df[
    "transaction_date"
].dt.strftime("%Y-%m-%d %H:%M:%S")


# 8. Crear archivos

clean_df.to_csv(
    CLEAN_FILE,
    index=False
)

rejected_df.to_csv(
    REJECTED_FILE,
    index=False
)


# 9. Resultado

print()
print("ETL completado")
print(f"Registros RAW:       {len(df)}")
print(f"Registros CLEAN:     {len(clean_df)}")
print(f"Registros REJECTED:  {len(rejected_df)}")
print(f"Total procesado:     {total_processed}")
print()
print(f"Archivo CLEAN:       {CLEAN_FILE}")
print(f"Archivo REJECTED:    {REJECTED_FILE}")