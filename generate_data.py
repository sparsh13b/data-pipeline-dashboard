"""
generate_data.py
generates sample csv files with some messy data so we have something to clean.
run this first before clean_data.py
"""

import csv
import random
import os
from pathlib import Path
from datetime import datetime, timedelta

random.seed(42)

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


# --- helpers ---

def random_date(start, end, fmt="%Y-%m-%d"):
    """pick a random date between start and end"""
    delta = end - start
    rand_days = random.randint(0, delta.days)
    dt = start + timedelta(days=rand_days)
    return dt.strftime(fmt)


def mess_up_date(date_str):
    """randomly reformat a date to simulate messy data"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"]
    return dt.strftime(random.choice(formats))


# --- products ---

products = [
    ("P001", "Laptop", "Electronics", 999.99),
    ("P002", "Wireless Mouse", "Electronics", 29.99),
    ("P003", "Keyboard", "Electronics", 79.99),
    ("P004", "Monitor", "Electronics", 349.99),
    ("P005", "USB Cable", "Accessories", 9.99),
    ("P006", "Phone Case", "Accessories", 19.99),
    ("P007", "Headphones", "Audio", 149.99),
    ("P008", "Bluetooth Speaker", "Audio", 89.99),
    ("P009", "Webcam", "Electronics", 69.99),
    ("P010", "Desk Lamp", "Home Office", 39.99),
    ("P011", "Chair Mat", "Home Office", 49.99),
    ("P012", "Notebook", "Stationery", 5.99),
    ("P013", "Pen Set", "Stationery", 12.99),
    ("P014", "Backpack", "Accessories", 59.99),
    ("P015", "External SSD", "Electronics", 119.99),
    ("P016", "HDMI Cable", "Accessories", 14.99),
    ("P017", "Mouse Pad", "Accessories", 11.99),
    ("P018", "Standing Desk", "Home Office", 499.99),
    ("P019", "Earbuds", "Audio", 59.99),
    ("P020", "Power Bank", "Electronics", 34.99),
    ("P021", "Tablet Stand", "Accessories", 24.99),
    ("P022", "Whiteboard", "Home Office", 44.99),
    ("P023", "Marker Set", "Stationery", 8.99),
    ("P024", "Surge Protector", "Electronics", 27.99),
    ("P025", "Cable Organizer", "Accessories", 15.99),
]

# write products.csv
with open(RAW_DIR / "products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["product_id", "product_name", "category", "unit_price"])
    for p in products:
        writer.writerow(p)

print(f"wrote {len(products)} products to {RAW_DIR / 'products.csv'}")


# --- customers ---

first_names = [
    "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank",
    "Iris", "Jack", "Karen", "Leo", "Mona", "Nate", "Olivia", "Paul",
    "Quinn", "Rachel", "Sam", "Tina", "Uma", "Victor", "Wendy", "Xander",
    "Yara", "Zach", "Arun", "Priya", "Ravi", "Sneha", "Amit", "Neha",
    "Vikram", "Anita", "Deepak", "Suman", "Kiran", "Pooja", "Rajesh", "Meera"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor", "Thomas", "Moore",
    "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Sharma",
    "Patel", "Kumar", "Singh", "Gupta", "Verma", "Reddy", "Nair", "Rao", "Das"
]

regions = ["North", "South", "East", "West", "Central"]
domains = ["gmail.com", "yahoo.com", "outlook.com", "company.co", "mail.com"]

customers = []
customer_ids = []

for i in range(1, 181):
    cid = f"C{i:04d}"
    customer_ids.append(cid)
    fname = random.choice(first_names)
    lname = random.choice(last_names)

    # sometimes add leading/trailing whitespace to name
    name = f"{fname} {lname}"
    if random.random() < 0.1:
        name = f"  {name} "

    # generate email, sometimes make it bad
    r = random.random()
    if r < 0.05:
        email = ""  # missing email
    elif r < 0.10:
        email = f"{fname.lower()}{lname.lower()}"  # no @ or dot
    elif r < 0.15:
        email = f"{fname.upper()}.{lname.upper()}@{random.choice(domains)}"  # uppercase
    else:
        email = f"{fname.lower()}.{lname.lower()}@{random.choice(domains)}"

    # region - sometimes missing
    region = random.choice(regions) if random.random() > 0.08 else ""

    # sometimes add whitespace to region
    if region and random.random() < 0.1:
        region = f" {region} "

    signup = random_date(datetime(2021, 1, 1), datetime(2025, 12, 31))

    # sometimes mess up the date format
    if random.random() < 0.08:
        signup = "not-a-date"

    customers.append([cid, name, email, region, signup])

# add some duplicate customer_ids with older dates to test dedup
for _ in range(20):
    orig = random.choice(customers[:150])
    dup = orig.copy()
    # give it an older signup date
    dup[4] = random_date(datetime(2019, 1, 1), datetime(2020, 12, 31))
    # maybe tweak the name slightly
    if random.random() < 0.5:
        dup[1] = dup[1].strip()
    customers.append(dup)

random.shuffle(customers)

with open(RAW_DIR / "customers.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["customer_id", "name", "email", "region", "signup_date"])
    for c in customers:
        writer.writerow(c)

print(f"wrote {len(customers)} customer rows (with dupes) to {RAW_DIR / 'customers.csv'}")


# --- orders ---

product_names = [p[1] for p in products]
statuses_normal = ["completed", "pending", "cancelled", "refunded"]
# messy variants that should map to the above
statuses_messy = [
    "done", "COMPLETED", "Complete", "Completed",
    "Pending", "PENDING", "pend",
    "canceled", "Cancelled", "CANCELLED", "cancel",
    "refunded", "Refunded", "REFUNDED", "refund",
]
all_statuses = statuses_normal + statuses_messy

orders = []

for i in range(1, 1001):
    oid = f"O{i:05d}"
    cid = random.choice(customer_ids)

    product = random.choice(product_names)

    # amount - usually based on product price but with some noise
    base_price = next(p[3] for p in products if p[1] == product)
    qty = random.randint(1, 5)
    amount = round(base_price * qty + random.uniform(-5, 20), 2)

    # sometimes null amount
    if random.random() < 0.07:
        amount = ""

    order_date = random_date(datetime(2023, 1, 1), datetime(2025, 11, 30))
    order_date = mess_up_date(order_date)

    # sometimes make date bad
    if random.random() < 0.03:
        order_date = ""

    status = random.choice(all_statuses)

    orders.append([oid, cid, product, amount, order_date, status])

# add a few completely junk rows (both oid and cid are null)
for _ in range(5):
    orders.append(["", "", random.choice(product_names), "", "", "pending"])

random.shuffle(orders)

with open(RAW_DIR / "orders.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["order_id", "customer_id", "product", "amount", "order_date", "status"])
    for o in orders:
        writer.writerow(o)

print(f"wrote {len(orders)} order rows to {RAW_DIR / 'orders.csv'}")
print("\ndone! raw csvs are in:", RAW_DIR)
