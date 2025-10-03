import json
import os

RULES_FILE = os.path.join(os.path.dirname(__file__), "rules.json")

def load_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_rules(ctx):
    findings = []

    # Make sure we’re iterating over transaction dicts
    transactions = ctx.get("transactions", [])
    if isinstance(transactions, str):
        # If somehow it’s a single string, skip
        return findings

    for txn in transactions:
        if not isinstance(txn, dict):
            continue  # skip anything malformed

        desc = txn.get("description", "").lower()
        amount = txn.get("amount", 0.0)

        # Example rules
        if "wages" in desc or "salary" in desc:
            findings.append({
                "name": "Check Employment Allowance eligibility",
                "why": "You appear to have payroll costs",
                "how_to_do_it": "If eligible, reduce employer NICs by the allowance in your PAYE software",
                "estimated_saving": 5000,
                "hmrc_link": "https://www.gov.uk/claim-employment-allowance",
                "evidence_examples": [desc]
            })

        if "machine" in desc or "equipment" in desc or "furniture" in desc:
            findings.append({
                "name": "Claim AIA on qualifying plant and machinery",
                "why": "You bought assets that likely qualify for capital allowances",
                "how_to_do_it": "Add them to your main pool and claim a 100% deduction this year if eligible",
                "estimated_saving": amount * 0.2,  # rough estimate
                "hmrc_link": "https://www.gov.uk/capital-allowances/annual-investment-allowance",
                "evidence_examples": [f"{txn.get('date')} {desc} {amount}"]
            })

    return findings