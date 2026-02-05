from __future__ import annotations
import pandas as pd


def compute_actions(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["TotalInv"] = out["OnHandQty"] + out.get("TotalPOQty", 0)
    out["Action"] = "No Action"
    out["Calculated_Quantity"] = 0

    order = out["TotalInv"] < out["ReorderPoint"]
    reduce = out["TotalInv"] > (out["ReorderPoint"] + out["EOQ"])

    out.loc[order, "Action"] = "Order"
    out.loc[order, "Calculated_Quantity"] = out.loc[order, "EOQ"]

    out.loc[reduce, "Action"] = "Reduce Stock"
    out.loc[reduce, "Calculated_Quantity"] = out.loc[reduce, "TotalInv"] - (out.loc[reduce, "ReorderPoint"] + out.loc[reduce, "EOQ"])

    out["ChangeValue"] = out["Calculated_Quantity"] * out["UnitCost"]
    return out
