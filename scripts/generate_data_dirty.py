import json
import random
import csv
import os

from datetime import datetime, timedelta
from faker import Faker


fake = Faker("it_IT")
random.seed(42)

os.makedirs("data/raw", exist_ok=True)

N_CUSTOMERS = 5_000
N_PRODUCTS = 300
N_ORDERS = 100_000

CATEGORIES = [
    "elettronica",
    "casa",
    "moda",
    "sport",
    "libri",
]


# ---------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------

with open("data/raw/customers.csv", "w", newline="") as f:
    w = csv.writer(f)

    w.writerow([
        "customer_id",
        "name",
        "email",
        "city",
        "signup_date",
    ])

    for i in range(1, N_CUSTOMERS + 1):
        w.writerow([
            i,
            fake.name(),
            fake.email(),
            fake.city(),
            fake.date_between("-3y", "today"),
        ])


# ---------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------

with open("data/raw/products.csv", "w", newline="") as f:
    w = csv.writer(f)

    w.writerow([
        "product_id",
        "name",
        "category",
        "price",
    ])

    for i in range(1, N_PRODUCTS + 1):
        w.writerow([
            i,
            fake.word(),
            random.choice(CATEGORIES),
            round(random.uniform(5, 800), 2),
        ])


# ---------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------

start = datetime.now() - timedelta(days=90)

orders = []

for i in range(1, N_ORDERS + 1):

    ts = start + timedelta(
        seconds=random.randint(0, 90 * 86400)
    )

    order = {
        "order_id": i,
        "customer_id": random.randint(1, N_CUSTOMERS),
        "product_id": random.randint(1, N_PRODUCTS),
        "quantity": random.randint(1, 5),
        "status": random.choices(
            ["completed", "failed", "refunded"],
            [0.9, 0.06, 0.04],
        )[0],
        "channel": random.choice(
            ["web", "app", "marketplace"]
        ),
        "order_ts": ts.isoformat(),
    }

    # -------------------------------------------------------------
    # Anomalia 1: customer_id nullo
    # ~0.2% degli ordini
    # -------------------------------------------------------------

    if random.random() < 0.002:
        order["customer_id"] = None

    # -------------------------------------------------------------
    # Anomalia 2: quantity negativa
    # ~0.2% degli ordini
    # -------------------------------------------------------------

    if random.random() < 0.002:
        order["quantity"] = -random.randint(1, 5)

    # -------------------------------------------------------------
    # Anomalia 3: product_id inesistente
    # ~0.2% degli ordini
    #
    # I product_id validi sono 1..300.
    # Questi valori saranno quindi sicuramente invalidi.
    # -------------------------------------------------------------

    if random.random() < 0.002:
        order["product_id"] = N_PRODUCTS + random.randint(1, 100)

    orders.append(order)


# ---------------------------------------------------------------------
# Anomalia 4: duplicati / retry della sorgente
# ---------------------------------------------------------------------
#
# Duplichiamo circa lo 0.2% degli ordini.
# Il retry mantiene lo stesso order_id ma modifica leggermente order_ts.
#

N_DUPLICATES = int(N_ORDERS * 0.002)

duplicate_orders = []

for original in random.sample(orders, N_DUPLICATES):

    duplicate = original.copy()

    original_ts = datetime.fromisoformat(
        duplicate["order_ts"]
    )

    # Retry avvenuto da 1 a 60 secondi dopo
    retry_ts = original_ts + timedelta(
        seconds=random.randint(1, 60)
    )

    duplicate["order_ts"] = retry_ts.isoformat()

    duplicate_orders.append(duplicate)


# Aggiungiamo i retry agli ordini originali
orders.extend(duplicate_orders)

# Mischiamo tutto per evitare che i duplicati
# siano semplicemente in fondo al file
random.shuffle(orders)


# ---------------------------------------------------------------------
# Scrittura JSONL
# ---------------------------------------------------------------------

with open("data/raw/orders.jsonl", "w") as f:
    for order in orders:
        f.write(json.dumps(order) + "\n")


print("done")
print(f"customers: {N_CUSTOMERS}")
print(f"products: {N_PRODUCTS}")
print(f"orders originali: {N_ORDERS}")
print(f"retry/duplicati aggiunti: {N_DUPLICATES}")
print(f"righe orders.jsonl: {len(orders)}")