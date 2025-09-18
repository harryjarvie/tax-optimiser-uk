import csv, io
from typing import List, Dict

REQUIRED = ["date", "description", "amount", "account"]

def parse_bank_csv(file_bytes: bytes) -> List[Dict]:
    text = file_bytes.decode("utf-8").strip()
    rows = []
    reader = csv.DictReader(io.StringIO(text))
    for r in reader:
        for k in REQUIRED:
            if k not in r or r[k] is None or r[k] == "":
                raise ValueError("Missing column " + k)
        rows.append({
            "date": r["date"],
            "description": r["description"],
            "amount": float(r["amount"]),
            "account": r["account"]
        })
    return rows
