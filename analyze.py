"""
analyze.py
merges the cleaned datasets and produces analysis csvs.
reads from data/processed/ and outputs back there.

usage: python analyze.py
"""

import pandas as pd
import argparse
from pathlib import Path


# ---- config ----

# default paths, can be overridden via argparse
DEFAULT_CONFIG = {
    "customers_clean": "data/processed/customers_clean.csv",
    "orders_clean": "data/processed/orders_clean.csv",
    "products": "data/raw/products.csv",
    "output_dir": "data/processed",
}


# ---- helpers ----

def load_csv(filepath):
    """
    load a csv with basic error handling.
    returns a dataframe or raises an error with a helpful message.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"could not find file: {path}")

    df = pd.read_csv(path)
    if df.empty:
        raise pd.errors.EmptyDataError(f"file is empty: {path}")

    return df


def setup_args():
    """parse command line args for file paths"""
    parser = argparse.ArgumentParser(description="merge and analyze cleaned data")
    parser.add_argument("--customers", default=DEFAULT_CONFIG["customers_clean"],
                        help="path to cleaned customers csv")
    parser.add_argument("--orders", default=DEFAULT_CONFIG["orders_clean"],
                        help="path to cleaned orders csv")
    parser.add_argument("--products", default=DEFAULT_CONFIG["products"],
                        help="path to products csv")
    parser.add_argument("--output", default=DEFAULT_CONFIG["output_dir"],
                        help="output directory for analysis csvs")
    return parser.parse_args()


# ---- merging ----

def merge_data(customers, orders, products):
    """
    merge the three datasets together.
    returns the full merged dataframe.
    """
    # left join orders onto customers
    orders_with_customers = pd.merge(
        orders,
        customers,
        on="customer_id",
        how="left",
        suffixes=("", "_customer")
    )

    # count orders with no matching customer
    no_customer = orders_with_customers["name"].isna().sum()
    print(f"orders with no matching customer: {no_customer}")

    # left join products onto the result
    # orders have 'product' column, products have 'product_name'
    full_data = pd.merge(
        orders_with_customers,
        products,
        left_on="product",
        right_on="product_name",
        how="left",
        suffixes=("", "_product")
    )

    no_product = full_data["product_id"].isna().sum()
    print(f"orders with no matching product: {no_product}")

    return full_data


# ---- analysis functions ----

def monthly_revenue(df, output_dir):
    """
    compute total revenue from completed orders, grouped by month.
    """
    completed = df[df["status"] == "completed"].copy()
    monthly = completed.groupby("order_year_month", as_index=False)["amount"].sum()
    monthly.columns = ["month", "revenue"]
    monthly = monthly.sort_values("month").reset_index(drop=True)

    out = output_dir / "monthly_revenue.csv"
    monthly.to_csv(out, index=False)
    print(f"saved monthly revenue ({len(monthly)} rows) to {out}")
    return monthly


def top_customers(df, output_dir, latest_date):
    """
    find top 10 customers by total spend on completed orders.
    also flags churned customers (no completed order in past 90 days).
    """
    completed = df[df["status"] == "completed"].copy()

    # total spend per customer
    customer_spend = completed.groupby(
        ["customer_id", "name", "region"], as_index=False
    )["amount"].sum()
    customer_spend.columns = ["customer_id", "name", "region", "total_spend"]
    customer_spend = customer_spend.sort_values("total_spend", ascending=False)

    top10 = customer_spend.head(10).copy()

    # churn indicator: no completed orders in last 90 days
    cutoff = latest_date - pd.Timedelta(days=90)

    # get last completed order date per customer
    last_order = completed.groupby("customer_id")["order_date"].max().reset_index()
    last_order.columns = ["customer_id", "last_order_date"]

    top10 = pd.merge(top10, last_order, on="customer_id", how="left")
    top10["churned"] = top10["last_order_date"] < cutoff
    top10 = top10.drop(columns=["last_order_date"])

    top10 = top10.reset_index(drop=True)

    out = output_dir / "top_customers.csv"
    top10.to_csv(out, index=False)
    print(f"saved top 10 customers to {out}")
    return top10


def category_performance(df, output_dir):
    """
    group by product category, compute revenue, avg order value, and count.
    """
    completed = df[df["status"] == "completed"].copy()

    cats = completed.groupby("category", as_index=False).agg(
        total_revenue=("amount", "sum"),
        avg_order_value=("amount", "mean"),
        num_orders=("amount", "count")
    )
    cats["avg_order_value"] = cats["avg_order_value"].round(2)

    out = output_dir / "category_performance.csv"
    cats.to_csv(out, index=False)
    print(f"saved category performance ({len(cats)} rows) to {out}")
    return cats


def regional_analysis(df, output_dir):
    """
    group by region: number of customers, orders, total revenue, avg revenue per customer.
    """
    completed = df[df["status"] == "completed"].copy()

    regions = completed.groupby("region", as_index=False).agg(
        num_customers=("customer_id", "nunique"),
        num_orders=("order_id", "count"),
        total_revenue=("amount", "sum"),
    )
    regions["avg_revenue_per_customer"] = (
        regions["total_revenue"] / regions["num_customers"]
    ).round(2)

    out = output_dir / "regional_analysis.csv"
    regions.to_csv(out, index=False)
    print(f"saved regional analysis ({len(regions)} rows) to {out}")
    return regions


# ---- main ----

def main():
    args = setup_args()
    base = Path(__file__).parent

    print("loading datasets...\n")
    customers = load_csv(base / args.customers)
    orders = load_csv(base / args.orders)
    products = load_csv(base / args.products)

    output_dir = base / Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # make sure order_date is datetime
    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")

    print("\nmerging datasets...")
    full_data = merge_data(customers, orders, products)

    # latest date in the dataset for churn calc
    latest_date = full_data["order_date"].max()
    print(f"latest order date in dataset: {latest_date}\n")

    print("running analysis...\n")
    monthly_revenue(full_data, output_dir)
    top_customers(full_data, output_dir, latest_date)
    category_performance(full_data, output_dir)
    regional_analysis(full_data, output_dir)

    print(f"\nall analysis outputs saved to {output_dir}")


if __name__ == "__main__":
    main()
