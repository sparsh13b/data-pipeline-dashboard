"""
app.py
backend api for the dashboard. reads the processed csvs and serves them as json.
run with: uvicorn app:app --reload --port 8000
"""

import pandas as pd
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Data Pipeline Dashboard API")

# allow frontend to call from different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# path to processed csvs - relative to this file's parent dir
DATA_DIR = Path(__file__).parent.parent / "data" / "processed"


def read_csv_file(filename):
    """
    helper to read a csv and return as list of dicts.
    raises 404 if file not found.
    """
    filepath = DATA_DIR / filename
    if not filepath.exists():
        raise HTTPException(
            status_code=404,
            detail=f"data file not found: {filename}. did you run clean_data.py and analyze.py first?"
        )
    try:
        df = pd.read_csv(filepath)
        # replace NaN with None so json serialization works
        df = df.where(df.notna(), None)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error reading {filename}: {str(e)}")


@app.get("/health")
def health_check():
    """simple health check"""
    return {"status": "ok"}


@app.get("/api/revenue")
def get_revenue():
    """monthly revenue trend data"""
    return read_csv_file("monthly_revenue.csv")


@app.get("/api/top-customers")
def get_top_customers():
    """top 10 customers by spend"""
    return read_csv_file("top_customers.csv")


@app.get("/api/categories")
def get_categories():
    """category performance breakdown"""
    return read_csv_file("category_performance.csv")


@app.get("/api/regions")
def get_regions():
    """regional analysis data"""
    return read_csv_file("regional_analysis.csv")
