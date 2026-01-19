from __future__ import annotations
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Dict, List, Tuple, Set
from .io import Record

@dataclass
class InputStats:
    filename: str
    num_sequences: int          # D
    num_transactions: int       # T (events)
    num_distinct_items: int     # I

    min_tx_per_seq: int
    max_tx_per_seq: int
    mean_tx_per_seq: float
    std_tx_per_seq: float

    min_items_per_tx: int
    max_items_per_tx: int
    mean_items_per_tx: float
    std_items_per_tx: float


def compute_input_stats(records: List[Record], filename: str) -> InputStats:
    if not records:
        raise ValueError("No records loaded.")

    sids: Set[int] = set()
    all_items: Set[str] = set()
    tx_per_sid: Dict[int, int] = {}
    items_per_tx: List[int] = []

    for r in records:
        sids.add(r.sid)
        tx_per_sid[r.sid] = tx_per_sid.get(r.sid, 0) + 1
        items_per_tx.append(len(r.items))
        all_items.update(r.items)

    tx_counts = list(tx_per_sid.values())

    return InputStats(
        filename=filename,
        num_sequences=len(sids),
        num_transactions=len(records),
        num_distinct_items=len(all_items),

        min_tx_per_seq=min(tx_counts),
        max_tx_per_seq=max(tx_counts),
        mean_tx_per_seq=float(mean(tx_counts)),
        std_tx_per_seq=float(pstdev(tx_counts)) if len(tx_counts) > 1 else 0.0,

        min_items_per_tx=min(items_per_tx),
        max_items_per_tx=max(items_per_tx),
        mean_items_per_tx=float(mean(items_per_tx)),
        std_items_per_tx=float(pstdev(items_per_tx)) if len(items_per_tx) > 1 else 0.0,
    )
