import csv
import io

def parse_bank_csv(data: bytes):
    # Decode bytes into text
    if isinstance(data, bytes):
        text = data.decode("utf-8")
    else:
        text = str(data)

    f = io.StringIO(text)
    reader = csv.DictReader(f)

    if not reader.fieldnames:
        raise ValueError("CSV file is missing headers")

    # Normalize headers (lowercase, strip spaces)
    fieldnames = [h.strip().lower() for h in reader.fieldnames]
    mapping = {}

    # Map flexible header names to standard ones
    for i, h in enumerate(fieldnames):
        if h in ["date", "transaction date", "txn date"]:
            mapping["date"] = reader.fieldnames[i]
        elif h in ["description", "details", "narrative", "info"]:
            mapping["description"] = reader.fieldnames[i]
        elif h in ["amount", "value", "debit", "credit", "debit/credit"]:
            mapping["amount"] = reader.fieldnames[i]

    # Force fallback if common headers exist
    if "description" not in mapping and "Details" in reader.fieldnames:
        mapping["description"] = "Details"
    if "amount" not in mapping and "Value" in reader.fieldnames:
        mapping["amount"] = "Value"
    if "date" not in mapping and "Transaction Date" in reader.fieldnames:
        mapping["date"] = "Transaction Date"

    # Check for required fields
    required = ["date", "description", "amount"]
    for k in required:
        if k not in mapping:
            raise ValueError(f"Missing column: {k}")

    # Build rows
    rows = []
    for row in reader:
        try:
            amount = float(row[mapping["amount"]].replace(",", "").strip())
        except Exception:
            amount = 0.0  # fallback if not convertible

        rows.append({
            "date": row[mapping["date"]].strip(),
            "description": row[mapping["description"]].strip(),
            "amount": amount
        })

    print("DEBUG: Parsed rows ->", rows)
    return rows