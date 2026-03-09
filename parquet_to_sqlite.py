########################################################################################################
# Dipen Patel
# Date: 10/28/2024
# Load parquet file(s) and dump into a SQLite DB in the same folder.
# Place files in unprocessed/; script moves them to processed/ or failed/, logs to processing_log.log.
# Run manually each time (not automated). View parquet_view.db with any SQLite tool.
########################################################################################################

"""
Prerequisites:
  pip install pandas pyarrow
"""

import pandas as pd
import sqlite3
import os
import datetime
import shutil
import logging
import decimal

# Set base_path for your machine (or use env PARQUET_BASE_PATH)
base_path = os.environ.get("PARQUET_BASE_PATH", r"C:\DP-Temp\parquet_test")
unprocessed_folder = os.path.join(base_path, "unprocessed")
processed_folder = os.path.join(base_path, "processed")
failed_folder = os.path.join(base_path, "failed")
sqlite_db_path = os.path.join(base_path, "parquet_view.db")
log_file_path = os.path.join(base_path, "processing_log.log")

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

os.makedirs(unprocessed_folder, exist_ok=True)
os.makedirs(processed_folder, exist_ok=True)
os.makedirs(failed_folder, exist_ok=True)

maintenance_table = "file_processing_log"
column_info_table = "file_column_info"

for filename in os.listdir(unprocessed_folder):
    if not filename.endswith(".parquet"):
        continue
    parquet_file_path = os.path.join(unprocessed_folder, filename)
    table_name = os.path.splitext(filename)[0]

    try:
        df = pd.read_parquet(parquet_file_path, engine="pyarrow")

        for col in df.select_dtypes(include=["object", "float64"]):
            if df[col].apply(lambda x: isinstance(x, decimal.Decimal)).any():
                df[col] = df[col].astype(float)

        total_rows, total_columns = df.shape[0], df.shape[1]
        process_datetime = datetime.datetime.now()
        columns_info = [(col, str(df[col].dtype), idx + 1) for idx, col in enumerate(df.columns)]
        top_1000_df = df.head(1000)

        conn = sqlite3.connect(sqlite_db_path)
        cursor = conn.cursor()

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {maintenance_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                process_datetime TEXT,
                total_rows INTEGER,
                total_columns INTEGER,
                table_name TEXT
            )
        """)
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {column_info_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                column_name TEXT,
                data_type TEXT,
                column_sequence INTEGER,
                process_datetime TEXT
            )
        """)

        if not top_1000_df.empty:
            top_1000_df.to_sql(table_name, conn, if_exists="replace", index=False)
        else:
            logging.warning(f"{filename} is empty and was not added to the database.")

        cursor.execute(f"""
            INSERT INTO {maintenance_table} (filename, process_datetime, total_rows, total_columns, table_name)
            VALUES (?, ?, ?, ?, ?)
        """, (filename, process_datetime, total_rows, total_columns, table_name))

        for col_name, col_type, col_sequence in columns_info:
            cursor.execute(f"""
                INSERT INTO {column_info_table} (filename, column_name, data_type, column_sequence, process_datetime)
                VALUES (?, ?, ?, ?, ?)
            """, (filename, col_name, col_type, col_sequence, process_datetime))

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for (name,) in cursor.fetchall():
            if name in (maintenance_table, column_info_table):
                continue
            try:
                date_str = name.split("_")[-1]
                table_date = datetime.datetime.strptime(date_str, "%Y%m%d")
                if (datetime.datetime.now() - table_date).days > 7:
                    cursor.execute(f"DROP TABLE {name}")
                    print(f"Dropped table: {name} (older than a week)")
            except ValueError:
                continue

        conn.commit()
        conn.close()
        shutil.move(parquet_file_path, os.path.join(processed_folder, filename))
        logging.info(f"Successfully processed and moved {filename} to the processed folder.")

    except Exception as e:
        shutil.move(parquet_file_path, os.path.join(failed_folder, filename))
        logging.error(f"Failed to process {filename}. Error: {e}")
