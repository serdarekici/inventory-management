from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
from scipy.stats import norm


@dataclass(frozen=True)
class ServiceLevelPolicy:
    policy: Dict[str, float]

    @staticmethod
    def default() -> "ServiceLevelPolicy":
        # Tunable defaults (simple, explainable)
        return ServiceLevelPolicy(
            policy={
                "AL": 0.97, "AM": 0.97, "AH": 0.97,
                "BL": 0.93, "BM": 0.93, "BH": 0.93,
                "CL": 0.90, "CM": 0.90,
                "CH": 0.85,
            }
        )

    def get(self, nine_box: str) -> float:
        return float(self.policy.get(nine_box, 0.85))

    def z(self, nine_box: str) -> float:
        return float(norm.ppf(self.get(nine_box)))


def safety_stock(std_monthly: float, lead_time_days: float, z: float) -> int:
    lt_m = max(float(lead_time_days) / 30.0, 0.0)
    ss = z * float(std_monthly) * np.sqrt(lt_m)
    if not np.isfinite(ss) or ss < 0:
        return 0
    return int(round(ss))


def reorder_point(avg_monthly: float, lead_time_days: float, safety_stock_units: int) -> int:
    lt_m = max(float(lead_time_days) / 30.0, 0.0)
    rop = (float(avg_monthly) * lt_m) + int(safety_stock_units)
    if not np.isfinite(rop) or rop < 0:
        return 0
    return int(round(rop))


def eoq(annual_demand: float, ordering_cost: float, unit_cost: float, holding_rate: float = 0.2) -> int:
    h = float(unit_cost) * float(holding_rate)
    if h <= 0 or annual_demand <= 0 or ordering_cost <= 0:
        return 0
    q = np.sqrt((2.0 * float(annual_demand) * float(ordering_cost)) / h)
    if not np.isfinite(q) or q < 0:
        return 0
    return int(round(q))
