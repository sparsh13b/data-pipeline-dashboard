"""
clean_data.py
cleans up the raw csv files (customers.csv, orders.csv) and saves them
to data/processed/ as customers_clean.csv and orders_clean.csv.

also prints a cleaning report showing what changed.

usage: python clean_data.py
"""

import pandas as pd
import numpy as np
import warnings
import re
from pathlib import Path

# paths - using relative to script location, no hardcoding
BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ---- helper functions ----

def parse_date(val):
    """
    try parsing a date string in multiple formats.
    returns a pandas Timestamp or NaT if nothing works.
    """
    if pd.isna(val) or str(val).strip() == "":
        return pd.NaT

    val = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            pass

    # if we get here, none of the formats worked
    warnings.warn(f"could not parse date: '{val}', setting to NaT")
    return pd.NaT


def validate_email(email):
    """
    check if an email looks valid - has @ and at least one dot after @.
    returns True/False
    """
    if pd.isna(email) or str(email).strip() == "":
        return False

    email = str(email).strip()
    # simple check: must have @ and a . somewhere after it
    if "@" not in email:
        return False
    if "." not in email.split("@")[-1]:
        return False

    return True


def normalize_status(status):
    """
    map various status strings to a controlled set:
    completed, pending, cancelled, refunded
    """
    if pd.isna(status):
        return status

    s = str(status).strip().lower()

    # mapping for common variants
    status_map = {
        "completed": "completed",
        "complete": "completed",
        "done": "completed",
        "pending": "pending",
        "pend": "pending",
        "cancelled": "cancelled",
        "canceled": "cancelled",
        "cancel": "cancelled",
        "refunded": "refunded",
        "refund": "refunded",
    }

    return status_map.get(s, s)


def print_report(name, before_shape, after_shape, nulls_before, nulls_after, dupes_removed=0):
    """print a nice cleaning summary"""
    print(f"\n{'='*50}")
    print(f"  cleaning report: {name}")
    print(f"{'='*50}")
    print(f"  rows before: {before_shape[0]}")
    print(f"  rows after:  {after_shape[0]}")
    print(f"  duplicates removed: {dupes_removed}")
    print(f"\n  null counts before vs after:")
    print(f"  {'column':<25} {'before':>8} {'after':>8}")
    print(f"  {'-'*43}")

    all_cols = set(list(nulls_before.index) + list(nulls_after.index))
    for col in sorted(all_cols):
        before_val = nulls_before.get(col, 0)
        after_val = nulls_after.get(col, 0)
        print(f"  {col:<25} {before_val:>8} {after_val:>8}")
    print()


# ---- main cleaning logic ----

def clean_customers():
    """clean customers.csv according to the rules"""
    print("loading customers.csv...")
    df = pd.read_csv(RAW_DIR / "customers.csv")

    before_shape = df.shape
    nulls_before = df.isnull().sum()

    # replace empty strings with NaN for consistency
    df.replace("", np.nan, inplace=True)

    # strip whitespace from name and region
    df["name"] = df["name"].astype(str).str.strip()
    df["region"] = df["region"].astype(str).str.strip()

    # fix 'nan' strings that come from astype on NaN
    df["region"] = df["region"].replace("nan", np.nan)
    df["name"] = df["name"].replace("nan", np.nan)

    # fill missing region with 'Unknown'
    df["region"] = df["region"].fillna("Unknown")

    # parse signup_date
    df["signup_date"] = df["signup_date"].apply(parse_date)

    # remove duplicates on customer_id, keep the one with most recent signup_date
    # sort by signup_date descending so first occurrence is the latest
    df = df.sort_values("signup_date", ascending=False, na_position="last")
    dupes_removed = df.duplicated(subset="customer_id", keep="first").sum()
    df = df.drop_duplicates(subset="customer_id", keep="first")
    df = df.sort_values("customer_id").reset_index(drop=True)

    # standardize email to lowercase
    df["email"] = df["email"].astype(str).str.lower().str.strip()
    df["email"] = df["email"].replace("nan", np.nan)

    # flag invalid emails
    df["is_valid_email"] = df["email"].apply(validate_email)

    nulls_after = df.isnull().sum()
    after_shape = df.shape

    print_report("customers.csv", before_shape, after_shape, nulls_before, nulls_after, dupes_removed)

    # save
    out_path = PROCESSED_DIR / "customers_clean.csv"
    df.to_csv(out_path, index=False)
    print(f"saved cleaned customers to {out_path}")

    return df


def clean_orders():
    """clean orders.csv according to the rules"""
    print("loading orders.csv...")
    df = pd.read_csv(RAW_DIR / "orders.csv")

    before_shape = df.shape
    nulls_before = df.isnull().sum()

    # replace empty strings with NaN
    df.replace("", np.nan, inplace=True)

    # drop rows where both customer_id and order_id are null
    unrecoverable = df["customer_id"].isna() & df["order_id"].isna()
    dropped_count = unrecoverable.sum()
    df = df[~unrecoverable].copy()
    print(f"dropped {dropped_count} unrecoverable rows (both ids null)")

    # parse order_date with multi-format parser
    df["order_date"] = df["order_date"].apply(parse_date)

    # fill missing amount with median grouped by product
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    median_by_product = df.groupby("product")["amount"].transform("median")
    df["amount"] = df["amount"].fillna(median_by_product)

    # if still null (product has no valid amounts), fill with overall median
    overall_median = df["amount"].median()
    df["amount"] = df["amount"].fillna(overall_median)

    # normalize status
    df["status"] = df["status"].apply(normalize_status)

    # add year-month column
    df["order_year_month"] = df["order_date"].dt.strftime("%Y-%m")

    nulls_after = df.isnull().sum()
    after_shape = df.shape

    # the dupes removed here is from dropping unrecoverable rows
    print_report("orders.csv", before_shape, after_shape, nulls_before, nulls_after, dupes_removed=dropped_count)

    # save
    out_path = PROCESSED_DIR / "orders_clean.csv"
    df.to_csv(out_path, index=False)
    print(f"saved cleaned orders to {out_path}")

    return df


# ---- run it ----

if __name__ == "__main__":
    print("starting data cleaning...\n")

    customers = clean_customers()
    orders = clean_orders()

    print("\n" + "="*50)
    print("  all done! cleaned files are in:", PROCESSED_DIR)
    print("="*50)
