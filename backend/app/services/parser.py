import csv
from io import StringIO

HEADER_MAP = {
    "date": ["date", "transaction date", "posted date"],
    "description": ["description", "narrative", "details", "transaction"],
    "amount": ["amount", "value", "debit/credit", "transaction amount"]
}

def normalize_header(header: str) -> str:
    return header.strip().lower()

def find_column(header_row, expected_variants):
    if not header_row:
        return None
    for col in header_row:
        if normalize_header(col) in expected_variants:
            return col
    return None

def parse_bank_csv(file_content: str):
    if isinstance(file_content, bytes):
        file_content = file_content.decode("utf-8")

    reader = csv.DictReader(StringIO(file_content))

    date_col = find_column(reader.fieldnames, HEADER_MAP["date"])
    desc_col = find_column(reader.fieldnames, HEADER_MAP["description"])
    amt_col = find_column(reader.fieldnames, HEADER_MAP["amount"])

    if not (date_col and desc_col and amt_col):
        return {
            "error": f"CSV missing required columns. Found: {reader.fieldnames}. "
                     f"Expected something like: date ({HEADER_MAP['date']}), "
                     f"description ({HEADER_MAP['description']}), "
                     f"amount ({HEADER_MAP['amount']})."
        }

    transactions = []
    for row in reader:
        try:
            transactions.append({
                "date": row[date_col],
                "description": row[desc_col],
                "amount": float(row[amt_col].replace(",", ""))
            })
        except Exception as e:
            print(f"Skipping row {row}: {e}")
            continue

    return {"transactions": transactions}
