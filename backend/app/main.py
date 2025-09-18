from backend.app.data import models
from backend.app.data.database import engine

# Create tables on startup
models.Base.metadata.create_all(bind=engine)
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from backend.app.services.parser import parse_bank_csv
from backend.app.rules.engine import evaluate_rules, load_rules
from backend.app.services.store import Store

app = FastAPI(title="UK Tax Optimiser MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

store = Store()
rules = load_rules()

class BusinessIn(BaseModel):
    name: str
    entity_type: str
    vat_registered: bool

class PeriodIn(BaseModel):
    start_date: str
    end_date: str

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

@app.post("/upload/bank/{business_id}")
async def upload_bank(business_id: int, file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a CSV file")
    data = await file.read()
    rows = parse_bank_csv(data)
    count = store.add_transactions(business_id, rows)
    return {"rows_saved": count}

@app.get("/findings/{business_id}")
def findings(business_id: int):
    ctx = store.build_context(business_id)
    out = evaluate_rules(rules, ctx)
    return {"findings": out}
from fastapi import UploadFile, File
import os

UPLOAD_DIR = "backend/app/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

import pandas as pd
from backend.app.data import models
from backend.app.data.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

@app.post("/upload/bank/{business_id}")
async def upload_bank_csv(business_id: int, file: UploadFile = File(...)):
    # Accept both .csv and .txt (Safari often renames CSVs as .csv.txt)
    if not (file.filename.endswith(".csv") or file.filename.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    contents = await file.read()
    decoded = contents.decode("utf-8")

    # Always save with .csv extension, even if Safari renames it
    save_path = f"uploads/bank_{business_id}.csv"
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(decoded)

    return {"message": f"File saved successfully as {save_path}"}