import csv
import io

def parse_bank_csv(text: str):
    f = io.StringIO(text)
    reader = csv.DictReader(f)

    if not reader.fieldnames:
        raise ValueError("CSV file is missing headers")

    print("DEBUG: CSV Headers ->", reader.fieldnames)

    fieldnames = [h.strip().lower() for h in reader.fieldnames]
    mapping = {}

    for i, h in enumerate(fieldnames):
        if h in ["date", "transaction date", "txn date"]:
            mapping["date"] = reader.fieldnames[i]
        elif h in ["description", "details", "narrative", "info"]:
            mapping["description"] = reader.fieldnames[i]
        elif h in ["amount", "value", "debit", "credit", "debit/credit"]:
            mapping["amount"] = reader.fieldnames[i]

    required = ["date", "description", "amount"]
    for k in required:
        if k not in mapping:
            raise ValueError(f"Missing column: {k}")

    rows = []
    for row in reader:
        try:
            amount = float(row[mapping["amount"]].replace(",", "").strip())
        except Exception:
            amount = 0.0
        rows.append({
            "date": row[mapping["date"]].strip(),
            "description": row[mapping["description"]].strip(),
            "amount": amount
        })

    return rows