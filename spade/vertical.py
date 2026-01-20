from __future__ import annotations
from collections import defaultdict
from typing import Dict, List, Tuple
from .io import Record

Sid = int
Eid = int
Item = str
Tid = Tuple[Sid, Eid]
VerticalDB = Dict[Item, List[Tid]]

def build_vertical_db(records: List[Record]) -> VerticalDB:
    vdb: VerticalDB = defaultdict(list)
    for r in records:
        for it in r.items:
            vdb[it].append((r.sid, r.eid))

    # deterministic output
    for it in vdb:
        vdb[it].sort()
    return dict(vdb)

def support(tidlist: List[Tid]) -> int:
    # number of distinct sids in the tidlist
    return len({sid for sid, _ in tidlist})
