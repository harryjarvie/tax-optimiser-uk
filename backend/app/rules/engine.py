import json
import os

RULES_FILE = os.path.join(os.path.dirname(__file__), "rules.json")

def load_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_rules(transactions):
    rules = load_rules()
    findings = []

    for rule in rules:
        matched = []
        for txn in transactions:
            desc = txn["description"].lower()
            if any(keyword in desc for keyword in rule["keywords"]):
                matched.append(f"{txn['date']} {txn['description']} {txn['amount']}")

        if matched:
            saving = rule["estimated_saving"]
            if 0 < saving < 1:  # percentage of transaction
                estimated = abs(sum([txn["amount"] for txn in transactions if any(k in txn["description"].lower() for k in rule["keywords"])])) * saving
            else:
                estimated = saving

            findings.append({
                "name": rule["name"],
                "why": rule["why"],
                "how_to_do_it": rule["how_to_do_it"],
                "estimated_saving": round(estimated, 2),
                "hmrc_link": rule["hmrc_link"],
                "evidence_examples": matched
            })

    return {"findings": findings}