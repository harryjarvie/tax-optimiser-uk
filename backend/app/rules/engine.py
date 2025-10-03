import json
import os

RULES_FILE = os.path.join(os.path.dirname(__file__), "rules.json")

def load_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_rules(ctx):
    try:
        transactions = ctx.get("transactions", [])
        findings = []

        print("DEBUG: Transactions ->", transactions)

        for txn in transactions:
            # Ensure txn is always a dict
            if not isinstance(txn, dict):
                print("WARNING: Unexpected transaction format ->", txn)
                continue

            desc = str(txn.get("description", "")).lower()
            amount = float(txn.get("amount", 0) or 0)

            # Employment Allowance rule
            if any(keyword in desc for keyword in ["wages", "salary", "salaries", "payroll", "staff"]):
                findings.append({
                    "name": "Check Employment Allowance eligibility",
                    "why": "You appear to have payroll costs",
                    "how_to_do_it": "If eligible, reduce employer NICs by the allowance in your PAYE software",
                    "estimated_saving": 5000,
                    "hmrc_link": "https://www.gov.uk/claim-employment-allowance",
                    "evidence_examples": [txn.get("description", "N/A")]
                })

            # AIA rule
            if any(keyword in desc for keyword in ["machine", "equipment", "furniture", "computer", "laptop", "vehicle"]):
                findings.append({
                    "name": "Claim AIA on qualifying plant and machinery",
                    "why": "You bought assets that likely qualify for capital allowances",
                    "how_to_do_it": "Add them to your main pool and claim a 100% deduction this year if eligible",
                    "estimated_saving": amount * 0.2,
                    "hmrc_link": "https://www.gov.uk/capital-allowances/annual-investment-allowance",
                    "evidence_examples": [f"{txn.get('date')} {txn.get('description')} {amount}"]
                })

        return findings

    except Exception as e:
        print("ERROR in evaluate_rules:", e)
        return [{"error": str(e)}]
