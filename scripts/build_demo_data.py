from __future__ import annotations

import os

from src.inventory_optimization.sample_data import generate_sample_inventory, generate_sample_sales
from src.inventory_optimization.analysis import abc_classification, lmh_vod_classification, make_nine_box
from src.inventory_optimization.inventory_math import ServiceLevelPolicy, safety_stock, reorder_point, eoq
from src.inventory_optimization.recommendations import compute_actions


def main() -> None:
    out_dir = os.path.join("data", "sample")
    os.makedirs(out_dir, exist_ok=True)

    inv = generate_sample_inventory(n_parts=200)
    sales = generate_sample_sales(inv, months=36)

    abc = abc_classification(sales[["PartNum", "TotalValue"]])
    lmh = lmh_vod_classification(sales[["PartNum", "Date", "TotalDemand"]], months=36)
    nine = make_nine_box(abc, lmh)

    policy = ServiceLevelPolicy.default()

    merged = inv.merge(nine[["PartNum", "Category", "9_box"]], on="PartNum", how="left")
    merged["Category"] = merged["Category"].fillna("C")
    merged["9_box"] = merged["9_box"].fillna("CH")

    stats = lmh.set_index("PartNum")[["avg_usage", "std", "LMH", "vod"]]
    merged = merged.join(stats, on="PartNum")

    merged["ServiceLevel"] = merged["9_box"].apply(policy.get)
    merged["Z"] = merged["9_box"].apply(policy.z)

    merged["SafetyStock"] = merged.apply(lambda r: safety_stock(r["std"], r["LeadTimeDays"], r["Z"]), axis=1)
    merged["ReorderPoint"] = merged.apply(lambda r: reorder_point(r["avg_usage"], r["LeadTimeDays"], r["SafetyStock"]), axis=1)
    merged["EOQ"] = merged.apply(lambda r: eoq(r["avg_usage"] * 12.0, ordering_cost=50.0, unit_cost=r["UnitCost"], holding_rate=0.2), axis=1)

    merged.rename(columns={"avg_usage": "AvgMonthlyDemand", "std": "StdMonthlyDemand"}, inplace=True)

    params_cols = [
        "PartNum","Description","Category","LMH","9_box","vod",
        "AvgMonthlyDemand","StdMonthlyDemand","LeadTimeDays",
        "SafetyStock","ReorderPoint","EOQ",
        "OnHandQty","TotalPOQty","MinOrderQty","UnitCost","TotalValue","ServiceLevel"
    ]
    inventory_params = merged[params_cols].copy()
    rec = compute_actions(inventory_params)

    inv.to_csv(os.path.join(out_dir, "inventory.csv"), index=False)
    sales.to_csv(os.path.join(out_dir, "sales.csv"), index=False)
    inventory_params.to_csv(os.path.join(out_dir, "inventory_params.csv"), index=False)
    rec.to_csv(os.path.join(out_dir, "recommendations.csv"), index=False)

    print("Demo data generated under data/sample/")

if __name__ == "__main__":
    main()
