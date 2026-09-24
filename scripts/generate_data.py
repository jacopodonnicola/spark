import json, random, csv, os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("it_IT")
random.seed(42)
os.makedirs("data/raw", exist_ok=True)

N_CUSTOMERS, N_PRODUCTS, N_ORDERS = 5_000, 300, 100_000
CATEGORIES = ["elettronica", "casa", "moda", "sport", "libri"]

with open("data/raw/customers.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["customer_id", "name", "email", "city", "signup_date"])
    for i in range(1, N_CUSTOMERS + 1):
        w.writerow([i, fake.name(), fake.email(), fake.city(),
                    fake.date_between("-3y", "today")])

with open("data/raw/products.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["product_id", "name", "category", "price"])
    for i in range(1, N_PRODUCTS + 1):
        w.writerow([i, fake.word(), random.choice(CATEGORIES),
                    round(random.uniform(5, 800), 2)])

start = datetime.now() - timedelta(days=90)
with open("data/raw/orders.jsonl", "w") as f:
    for i in range(1, N_ORDERS + 1):
        ts = start + timedelta(seconds=random.randint(0, 90 * 86400))
        f.write(json.dumps({
            "order_id": i,
            "customer_id": random.randint(1, N_CUSTOMERS),
            "product_id": random.randint(1, N_PRODUCTS),
            "quantity": random.randint(1, 5),
            "status": random.choices(
                ["completed", "failed", "refunded"], [0.9, 0.06, 0.04])[0],
            "channel": random.choice(["web", "app", "marketplace"]),
            "order_ts": ts.isoformat(),
        }) + "\n")
print("done")