# Load an Excel file, parse date columns, drop rows with missing key columns.
# Usage: set FILE_PATH below or run with first arg: python excel_clean_dates.py path/to/file.xlsx
# Optional: edit DATE_COLUMNS and DROPNA_COLUMNS for your workbook.

import sys
import pandas as pd

FILE_PATH = r"C:\DP-Temp\EZPass\PAEZPass.xlsx"
DATE_COLUMNS = ["PostingDate", "EntryDate", "ExitDate"]
DROPNA_COLUMNS = ["EntryDate", "ExitDate", "Amount"]


def clean(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    if DROPNA_COLUMNS:
        df = df.dropna(subset=[c for c in DROPNA_COLUMNS if c in df.columns])
    return df


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else FILE_PATH
    df = clean(path)
    print(df.head())
    print(f"Rows: {len(df)}")
