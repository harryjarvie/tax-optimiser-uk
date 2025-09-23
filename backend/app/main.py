from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import pandas as pd

# Local imports
from backend.app.data import models
from backend.app.data.database import engine, get_db
from backend.app.services.parser import parse_bank_csv
from backend.app.rules.engine import evaluate_rules, load_rules
from backend.app.services.store import Store

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="UK Tax Optimiser MVP")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# In-memory store + load rules
store = Store()
rules = load_rules()

# ========== MODELS ==========

class BusinessIn(BaseModel):
    name: str
    entity_type: str
    vat_registered: bool

class PeriodIn(BaseModel):
    start_date: str
    end_date: str

# ========== ROUTES ==========

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/", response_class=HTMLResponse)
def home():
    with open("backend/app/templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/csv-guide", response_class=HTMLResponse)
def csv_guide():
    with open("backend/app/templates/csv_guide.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/action-plan", response_class=HTMLResponse)
def action_plan(business_id: int):
    with open("backend/app/templates/action_plan.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/business")
def create_business(body: BusinessIn):
    bid = store.create_business(body.name, body.entity_type, body.vat_registered)
    return {"business_id": bid}

@app.post("/period/{business_id}")
def create_period(business_id: int, body: PeriodIn):
    pid = store.create_period(business_id, body.start_date, body.end_date)
    return {"period_id": pid}

# ========== FIXED UPLOAD ENDPOINT ==========

@app.post("/upload/bank/{business_id}")
async def upload_bank(business_id: int, file: UploadFile = File(...)):
    try:
        if not (file.filename.endswith(".csv") or file.filename.endswith(".txt")):
            return {"status": "error", "message": f"Invalid file type: {file.filename}"}

        contents = await file.read()
        decoded = contents.decode("utf-8")

        result = parse_bank_csv(decoded)

        if "error" in result:
            return {"status": "error", "message": result["error"]}

        rows = result["transactions"]
        count = store.add_transactions(business_id, rows)

        return {
            "status": "success",
            "business_id": business_id,
            "transactions_uploaded": count,
            "sample": rows[:3]
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

# ========== FINDINGS ==========

@app.get("/findings/{business_id}")
def findings(business_id: int):
    ctx = store.build_context(business_id)
    out = evaluate_rules(rules, ctx)
    return {"findings": out}