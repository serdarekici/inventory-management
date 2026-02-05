from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ABCThresholds:
    a_pct: float = 75.0
    b_pct: float = 95.0


def abc_classification(sales_df: pd.DataFrame, thresholds: ABCThresholds = ABCThresholds()) -> pd.DataFrame:
    df = sales_df[["PartNum", "TotalValue"]].copy()
    df["TotalValue"] = df["TotalValue"].fillna(0.0)
    agg = df.groupby("PartNum", as_index=False)["TotalValue"].sum()
    agg = agg.sort_values("TotalValue", ascending=False)
    agg["CumulativeValue"] = agg["TotalValue"].cumsum()
    total = float(agg["TotalValue"].sum()) or 1.0
    agg["CumulativePercentage"] = 100.0 * agg["CumulativeValue"] / total

    def cat(p):
        if p <= thresholds.a_pct:
            return "A"
        if p <= thresholds.b_pct:
            return "B"
        return "C"

    agg["Category"] = agg["CumulativePercentage"].apply(cat)
    return agg[["PartNum", "TotalValue", "CumulativePercentage", "Category"]]


def lmh_vod_classification(
    sales_df: pd.DataFrame,
    months: int = 36,
    vod_thresholds: Tuple[float, float] = (2.0, 4.0),
    min_transactions: int = 3,
) -> pd.DataFrame:
    df = sales_df[["PartNum", "Date", "TotalDemand"]].copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M")

    today = pd.Timestamp.now()
    current_month_end = pd.Timestamp(today.year, today.month, 1) + pd.offsets.MonthEnd(0)
    start_date = current_month_end - pd.DateOffset(months=months - 1) - pd.offsets.MonthBegin(1)
    df = df[(df["Date"] >= start_date) & (df["Date"] <= current_month_end)]

    all_months = pd.period_range(start=start_date, end=current_month_end, freq="M")
    pivot = (
        df.pivot_table(index="PartNum", columns="Month", values="TotalDemand", aggfunc="sum")
        .reindex(columns=all_months)
        .fillna(0.0)
    )

    txn_counts = df.groupby("PartNum").size()

    pivot["std"] = pivot.iloc[:, :months].std(axis=1, ddof=1)
    pivot["avg_usage"] = pivot.iloc[:, :months].mean(axis=1)
    pivot["vod"] = np.where(pivot["avg_usage"] == 0, 0.0, pivot["std"] / pivot["avg_usage"])
    pivot["has_sufficient_data"] = txn_counts.reindex(pivot.index).fillna(0).ge(min_transactions)

    low_t, high_t = vod_thresholds
    conditions = [
        pivot["vod"] <= low_t,
        (pivot["vod"] > low_t) & (pivot["vod"] <= high_t),
        pivot["vod"] > high_t,
    ]
    pivot["LMH"] = np.select(conditions, ["L", "M", "H"], default="H")
    pivot.loc[~pivot["has_sufficient_data"], "LMH"] = "H"

    return pivot.reset_index()[["PartNum", "vod", "avg_usage", "std", "LMH"]]


def make_nine_box(abc_df: pd.DataFrame, lmh_df: pd.DataFrame) -> pd.DataFrame:
    df = abc_df.merge(lmh_df[["PartNum", "LMH"]], on="PartNum", how="left")
    df["LMH"] = df["LMH"].fillna("H")
    df["9_box"] = df["Category"] + df["LMH"]
    return df
