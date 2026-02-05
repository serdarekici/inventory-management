from __future__ import annotations
import numpy as np
import pandas as pd


def generate_sample_inventory(n_parts: int = 200, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    part_nums = [f"SP-{10000+i}" for i in range(n_parts)]
    unit_cost = rng.uniform(5, 500, size=n_parts).round(2)
    on_hand = rng.integers(0, 50, size=n_parts)
    lead_time = rng.integers(7, 120, size=n_parts)
    moq = rng.integers(0, 10, size=n_parts)
    po = rng.integers(0, 20, size=n_parts)

    inv = pd.DataFrame({
        "PartNum": part_nums,
        "Description": [f"Sample Part {i}" for i in range(n_parts)],
        "OnHandQty": on_hand,
        "UnitCost": unit_cost,
        "LeadTimeDays": lead_time,
        "MinOrderQty": moq,
        "TotalPOQty": po,
    })
    inv["TotalValue"] = inv["OnHandQty"] * inv["UnitCost"]
    return inv


def generate_sample_sales(inventory_df: pd.DataFrame, months: int = 36, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    parts = inventory_df["PartNum"].tolist()
    end = pd.Timestamp.now().normalize().replace(day=1) + pd.offsets.MonthEnd(0)
    start = end - pd.DateOffset(months=months-1) - pd.offsets.MonthBegin(1)
    all_months = pd.period_range(start=start, end=end, freq="M")

    rows = []
    for p in parts:
        base = float(inventory_df.loc[inventory_df["PartNum"] == p, "UnitCost"].iloc[0])
        lam = max(0.2, min(10.0, 300.0 / (base + 1.0)))
        for m in all_months:
            qty = rng.poisson(lam=lam)
            if rng.random() < 0.35:
                qty = 0
            unit_price = base * rng.uniform(1.2, 2.0)
            rows.append({
                "PartNum": p,
                "Date": m.to_timestamp(how="end"),
                "TotalDemand": int(qty),
                "UnitPrice": round(unit_price, 2),
                "Description": inventory_df.loc[inventory_df["PartNum"] == p, "Description"].iloc[0],
            })
    sales = pd.DataFrame(rows)
    sales["TotalValue"] = sales["TotalDemand"] * sales["UnitPrice"]
    return sales
