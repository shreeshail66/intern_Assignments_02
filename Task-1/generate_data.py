import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

N = 3000

regions = ["North", "South", "East", "West", "Central"]
categories = ["Electronics", "Clothing", "Home & Kitchen", "Sports", "Books", "Beauty"]
payment_modes = ["Credit Card", "Debit Card", "UPI", "Cash", "Net Banking"]
channels = ["Online", "In-Store"]

category_base_price = {
    "Electronics": 250, "Clothing": 40, "Home & Kitchen": 80,
    "Sports": 60, "Books": 20, "Beauty": 35,
}

dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")

order_id = np.arange(100000, 100000 + N)
order_date = rng.choice(dates, size=N)
region = rng.choice(regions, size=N, p=[0.22, 0.2, 0.2, 0.2, 0.18])
category = rng.choice(categories, size=N)
channel = rng.choice(channels, size=N, p=[0.65, 0.35])
payment_mode = rng.choice(payment_modes, size=N)

quantity = rng.integers(1, 12, size=N).astype(float)
unit_price = np.array([
    max(2, rng.normal(category_base_price[c], category_base_price[c] * 0.35))
    for c in category
])
unit_price = np.round(unit_price, 2)

discount_pct = np.round(rng.choice(
    [0, 0, 0, 5, 10, 15, 20, 25], size=N
).astype(float), 2)

customer_age = rng.integers(18, 70, size=N).astype(float)
customer_rating = np.round(rng.uniform(1, 5, size=N), 1)

df = pd.DataFrame({
    "OrderID": order_id,
    "OrderDate": order_date,
    "Region": region,
    "Category": category,
    "SalesChannel": channel,
    "PaymentMode": payment_mode,
    "Quantity": quantity,
    "UnitPrice": unit_price,
    "DiscountPercent": discount_pct,
    "CustomerAge": customer_age,
    "CustomerRating": customer_rating,
})

df["TotalSales"] = np.round(
    df["Quantity"] * df["UnitPrice"] * (1 - df["DiscountPercent"] / 100), 2
)


for col, frac in [("Quantity", 0.03), ("UnitPrice", 0.02), ("CustomerAge", 0.06),
                   ("CustomerRating", 0.04), ("Region", 0.015), ("PaymentMode", 0.02)]:
    idx = rng.choice(df.index, size=int(N * frac), replace=False)
    df.loc[idx, col] = np.nan

dup_idx = rng.choice(df.index, size=40, replace=False)
df = pd.concat([df, df.loc[dup_idx]], ignore_index=True)

df["Region"] = df["Region"].apply(
    lambda x: f"  {x.lower()} " if isinstance(x, str) and rng.random() < 0.15 else x
)
df["Category"] = df["Category"].apply(
    lambda x: x.upper() if isinstance(x, str) and rng.random() < 0.1 else x
)

def messy_number(v):
    if pd.isna(v):
        return v
    if rng.random() < 0.05:
        return str(v) 
    return v

df["Quantity"] = df["Quantity"].apply(messy_number)
df["CustomerAge"] = df["CustomerAge"].apply(messy_number)

neg_idx = rng.choice(df.index, size=15, replace=False)
df.loc[neg_idx, "Quantity"] = -abs(pd.to_numeric(df.loc[neg_idx, "Quantity"], errors="coerce").fillna(1))

out_idx = rng.choice(df.index, size=10, replace=False)
df.loc[out_idx, "UnitPrice"] = df.loc[out_idx, "UnitPrice"] * rng.uniform(15, 40)

def messy_date(d):
    d = pd.Timestamp(d)
    r = rng.random()
    if r < 0.1:
        return d.strftime("%d-%m-%Y")
    elif r < 0.2:
        return d.strftime("%m/%d/%Y")
    else:
        return d.strftime("%Y-%m-%d")

df["OrderDate"] = df["OrderDate"].apply(messy_date)

df = df.sample(frac=1, random_state=7).reset_index(drop=True)

df.to_csv("C:\Users\ACER\Downloads\devrise-task1\data\raw_retail_sales.csv", index=False)
print("Rows:", len(df))
print(df.dtypes)
print(df.isna().sum())
