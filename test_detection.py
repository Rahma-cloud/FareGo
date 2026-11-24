# Run from the repo root:  python test_detection.py
# This makes one real test payment (student 1 pays driver 1) in your database.
from lib.db import create_payment, get_fare
from lib.detection import check_duplicate

fare = get_fare()
print("Before paying:", check_duplicate(1, 1, fare))   # expect False
create_payment(1, 1, fare)
print("Right after paying:", check_duplicate(1, 1, fare))  # expect True
