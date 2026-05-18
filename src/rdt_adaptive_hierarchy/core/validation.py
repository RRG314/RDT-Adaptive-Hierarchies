from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationStatus:
    claim_id: str
    benchmark_status: str
    ablation_status: str
    real_data_status: str
    failure_condition: str

