import csv
from io import StringIO

# Possible header variations for each field
HEADER_MAP = {
    "date": ["date", "transaction date", "posted date"],
    "description": ["description", "narrative", "details", "transaction"],
    "amount": ["amount", "value", "debit/credit", "transaction amount"]
}

def normalize_header(header: str) -> str:
    """Convert header to lowercase and strip spaces for easier matching"""
    return header.strip().lower()

def find_column(header_row, expected_variants):
    """Try to find a column that matches one of the expected header names"""
    for col in header_row:
        norm = normalize_header(col)
        if norm in expected_variants:
            return col
    return None

def parse_bank_csv(file_content: str):
    reader = csv.DictReader(StringIO(file_content))

    # Detect which headers to use
    date_col = find_column(reader.fieldnames, HEADER_MAP["date"])
    desc_col = find_column(reader.fieldnames, HEADER_MAP["description"])
    amt_col = find_column(reader.fieldnames, HEADER_MAP["amount"])

    if not (date_col and desc_col and amt_col):
        raise ValueError(
            f"CSV must contain columns for date ({HEADER_MAP['date']}), "
            f"description ({HEADER_MAP['description']}), and "
            f"amount ({HEADER_MAP['amount']}). Found: {reader.fieldnames}"
        )

    transactions = []
    for row in reader:
        try:
            transactions.append({
                "date": row[date_col],
                "description": row[desc_col],
                "amount": float(row[amt_col].replace(",", ""))  # handle commas in numbers
            })
        except Exception as e:
            # Skip rows that can't be parsed properly
            print(f"Skipping row {row}: {e}")
            continue

    return transactions