import random
from datetime import datetime, timedelta

import bcrypt

from lib.db import get_conn

random.seed(7)
FARE = 200  # keep equal to the fare in the settings table

pw = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()
pin = bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode()

conn = get_conn()
cur = conn.cursor()


def add_user(name, email, role):
    cur.execute(
        "INSERT INTO users (full_name, email, password_hash, pin_hash, role) VALUES (%s, %s, %s, %s, %s)",
        (name, email, pw, pin, role),
    )
    return cur.lastrowid


def add_fare(student, driver, when, flagged=0):
    cur.execute(
        "INSERT INTO transactions (payer_user_id, payee_driver_id, amount, type, flagged_duplicate, created_at) "
        "VALUES (%s, %s, %s, 'fare', %s, %s)",
        (student, driver, FARE, flagged, when),
    )
    tx = cur.lastrowid
    cur.execute("INSERT INTO receipts (transaction_id, receipt_no) VALUES (%s, %s)", (tx, f"FG-{tx:06d}"))


students, drivers = [], []
for i in range(1, 21):
    uid = add_user(f"Student {i}", f"student{i}@test.com", "student")
    cur.execute("INSERT INTO wallets (user_id, balance) VALUES (%s, %s)", (uid, 5000))
    students.append(uid)

for i in range(1, 9):
    uid = add_user(f"Driver {i}", f"driver{i}@test.com", "driver")
    cur.execute("INSERT INTO wallets (user_id, balance) VALUES (%s, 0)", (uid,))
    cur.execute(
        "INSERT INTO drivers (user_id, bus_number, qr_code) VALUES (%s, %s, %s)",
        (uid, f"BUS-{i:02d}", f"DRV-{i:04d}"),
    )
    drivers.append(cur.lastrowid)

now = datetime.now()
for _ in range(200):
    when = now - timedelta(days=random.randint(0, 59), hours=random.randint(0, 10), minutes=random.randint(0, 59))
    add_fare(random.choice(students), random.choice(drivers), when)

# 5 deliberate duplicates: same student, driver and amount, 25 seconds apart
for _ in range(5):
    s, d = random.choice(students), random.choice(drivers)
    when = now - timedelta(days=random.randint(1, 20))
    add_fare(s, d, when)
    add_fare(s, d, when + timedelta(seconds=25), flagged=1)

conn.commit()
conn.close()
print("Seeded: 20 students, 8 drivers, about 210 transactions.")
