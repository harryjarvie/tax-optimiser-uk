#!/usr/bin/env bash
source .venv/bin/activate
uvicorn main:app --reload --app-dir backend/app

