from __future__ import annotations

from typing import Dict


def inherit_stable_labels(parent_label: int, new_label: int) -> tuple[int, int]:
    """Return child labels under the canonical stable inheritance rule.

    The left child preserves the parent label; the right child receives the next
    new label. This is the mechanism supported by ablation evidence.
    """

    return int(parent_label), int(new_label)


def relabel_by_active_order(active_nodes: Dict[int, int]) -> Dict[int, int]:
    """Non-stable control relabeling used in ablations."""

    return {node_id: i for i, node_id in enumerate(sorted(active_nodes))}

