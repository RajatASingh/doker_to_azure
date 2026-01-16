import pandas as pd
import random
from datetime import datetime, timedelta

# ---------------------------
# Configuration
# ---------------------------
NUM_CUSTOMERS = 220          # more than 200 customers
NUM_ORDERS = 1500            # total number of sales records
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)

# ---------------------------
# Generate customer names
# ---------------------------
customer_names = [f"Customer_{i}" for i in range(1, NUM_CUSTOMERS + 1)]

# ---------------------------
# Generate random dates
# ---------------------------
def random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

# ---------------------------
# Create sales data
# ---------------------------
data = []

for _ in range(NUM_ORDERS):
    customer = random.choice(customer_names)
    amount = round(random.uniform(500, 50000), 2)  # random sales amount
    order_date = random_date(START_DATE, END_DATE)

    data.append({
        "customer_name": customer,
        "total_amount": amount,
        "order_date": order_date
    })

# ---------------------------
# Create DataFrame
# ---------------------------
df = pd.DataFrame(data)

# Sort by date (optional but nice)
df.sort_values(by="order_date", inplace=True)

# ---------------------------
# Save files
# ---------------------------
df.to_csv("sales_data_1_year.csv", index=False)
df.to_excel("sales_data_1_year.xlsx", index=False)

print("Sales data generated successfully!")
