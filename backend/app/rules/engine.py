import os, yaml
from typing import List, Dict

def load_rules() -> List[Dict]:
    folder = "backend/app/rules"
    out = []
    for name in os.listdir(folder):
        if name.endswith(".yml") or name.endswith(".yaml"):
            with open(os.path.join(folder, name), "r") as f:
                out.append(yaml.safe_load(f))
    return out

def evaluate_rules(rules: List[Dict], ctx: Dict):
    txns = ctx["transactions"]
    business = ctx["business"]
    findings = []

    for r in rules:
        kind = r["kind"]

        if kind == "AIA":
            assets = [t for t in txns if "plant" in t.account.lower() or "equipment" in t.account.lower() or "machinery" in t.account.lower()]
            total = sum(max(t.amount, 0) for t in assets)
            if total > 0:
                findings.append({
                    "name": "Claim AIA on qualifying plant and machinery",
                    "why": "You bought assets that likely qualify for capital allowances",
                    "how_to_do_it": "Add them to your main pool and claim a 100% deduction this year if eligible",
                    "estimated_saving": round(total * 0.19, 2),
                    "hmrc_link": r["hmrc_link"],
                    "evidence_examples": [f"{a.date} {a.description} {a.amount}" for a in assets][:5]
                })

        if kind == "VAT_THRESHOLD":
            income = sum(t.amount for t in txns if t.amount > 0 and "sales" in t.account.lower())
            if income > r["threshold_hint"]:
                findings.append({
                    "name": "You may need to register for VAT or review your scheme",
                    "why": "Your sales look close to or above the VAT threshold",
                    "how_to_do_it": "Check last 12 months of sales. If above the threshold, register. Consider Flat Rate vs Standard method",
                    "estimated_saving": 0.0,
                    "hmrc_link": r["hmrc_link"],
                    "evidence_examples": [f"Estimated sales total {round(income,2)}"]
                })

        if kind == "EMPLOYMENT_ALLOWANCE":
            payroll_flag = any("wages" in t.account.lower() or "salaries" in t.account.lower() for t in txns)
            if payroll_flag and business.entity_type == "ltd":
                findings.append({
                    "name": "Check Employment Allowance eligibility",
                    "why": "You appear to have payroll costs",
                    "how_to_do_it": "If eligible, reduce employer NICs by the allowance in your PAYE software",
                    "estimated_saving": r["allowance_hint"],
                    "hmrc_link": r["hmrc_link"],
                    "evidence_examples": [t.account for t in txns if "wages" in t.account.lower() or "salaries" in t.account.lower()][:5]
                })
    return findings
