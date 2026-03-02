# Data Pipeline & Dashboard

A self-contained data pipeline project that ingests raw CSVs, cleans and transforms the data, runs analysis, and serves results through an interactive React dashboard.

## Project Structure

```
data-pipeline-dashboard/
├── generate_data.py          # generates sample raw CSVs (run first)
├── clean_data.py             # part 1: data cleaning
├── analyze.py                # part 2: merging & analysis
├── backend/
│   ├── app.py                # FastAPI REST API
│   └── requirements.txt      # python dependencies
├── frontend/                 # React + Vite dashboard
│   ├── src/
│   │   ├── main.jsx          # entry point
│   │   ├── App.jsx           # main dashboard component
│   │   ├── index.css         # global styles
│   │   └── components/
│   │       ├── RevenueChart.jsx
│   │       ├── TopCustomers.jsx
│   │       ├── CategoryChart.jsx
│   │       └── RegionSummary.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── data/
│   ├── raw/                  # original CSVs
│   └── processed/            # cleaned & analysis output CSVs
├── tests/
│   └── test_clean_data.py    # pytest unit tests
└── README.md
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- pip, npm

## Setup & Running

### 1. Install Python dependencies

```bash
pip install pandas numpy fastapi uvicorn pytest
```

### 2. Generate sample data

Since we don't have pre-supplied CSVs, run this first to create realistic sample data with deliberate dirty entries:

```bash
python generate_data.py
```

This creates `customers.csv`, `orders.csv`, and `products.csv` in `data/raw/`.

### 3. Run data cleaning (Part 1)

```bash
python clean_data.py
```

Outputs:
- `data/processed/customers_clean.csv`
- `data/processed/orders_clean.csv`
- Cleaning report printed to stdout

### 4. Run analysis (Part 2)

```bash
python analyze.py
```

Outputs in `data/processed/`:
- `monthly_revenue.csv`
- `top_customers.csv`
- `category_performance.csv`
- `regional_analysis.csv`

You can override file paths with arguments:
```bash
python analyze.py --customers path/to/customers.csv --orders path/to/orders.csv --products path/to/products.csv --output path/to/output/
```

### 5. Start the backend API (Part 3)

```bash
cd backend
uvicorn app:app --reload --port 8000
```

API endpoints:
- `GET /health` — health check
- `GET /api/revenue` — monthly revenue data
- `GET /api/top-customers` — top 10 customers
- `GET /api/categories` — category performance
- `GET /api/regions` — regional analysis

### 6. Start the frontend dashboard

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5500` in your browser.

### 7. Run tests (optional)

```bash
python -m pytest tests/ -v
```

## Dashboard Features

- **Revenue Trend** — Recharts area chart with date-range filter (bonus)
- **Top Customers** — sortable table with search box (bonus)
- **Category Breakdown** — bar chart of revenue by category
- **Region Summary** — card-based KPI view

## Assumptions

- Sample data is generated with a fixed random seed (42) for reproducibility.
- The "last 90 days" churn calculation is relative to the latest `order_date` in the dataset.
- Status normalization maps common variants (e.g., "done" → "completed", "canceled" → "cancelled"). Unrecognized statuses are kept as-is.
- For the multi-format date parser, when a date like "03-05-2024" is ambiguous, it's parsed as MM-DD-YYYY per the assignment spec.
- Missing `amount` values are filled with the median amount grouped by product; if a product has no valid amounts, the overall median is used.

## Tech Stack

- **Data processing**: Python, pandas, numpy
- **Backend**: FastAPI, uvicorn
- **Frontend**: React, Vite, Recharts
- **Testing**: pytest
