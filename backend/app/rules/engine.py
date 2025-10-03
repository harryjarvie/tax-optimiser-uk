import json
import os

RULES_FILE = os.path.join(os.path.dirname(__file__), "rules.json")

def load_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_rules(ctx):
    transactions = ctx.get("transactions", [])
    findings = []

    # Normalize descriptions to lowercase
    for txn in transactions:
        desc = txn["description"].lower()

        # Employment Allowance: any payroll-type costs
        if any(keyword in desc for keyword in ["wages", "salary", "salaries", "payroll", "staff"]):
            findings.append({
                "name": "Check Employment Allowance eligibility",
                "why": "You appear to have payroll costs",
                "how_to_do_it": "If eligible, reduce employer NICs by the allowance in your PAYE software",
                "estimated_saving": 5000,
                "hmrc_link": "https://www.gov.uk/claim-employment-allowance",
                "evidence_examples": [txn["description"]]
            })

        # Annual Investment Allowance: assets / equipment purchases
        if any(keyword in desc for keyword in ["machine", "equipment", "furniture", "computer", "laptop", "vehicle"]):
            findings.append({
                "name": "Claim AIA on qualifying plant and machinery",
                "why": "You bought assets that likely qualify for capital allowances",
                "how_to_do_it": "Add them to your main pool and claim a 100% deduction this year if eligible",
                "estimated_saving": float(txn["amount"]) * 0.2,  # estimate: 20% saving
                "hmrc_link": "https://www.gov.uk/capital-allowances/annual-investment-allowance",
                "evidence_examples": [f"{txn['date']} {txn['description']} {txn['amount']}"]
            })

    return findings
