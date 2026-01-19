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

    # deterministycznie: sortujemy tidlisty
    for it in vdb:
        vdb[it].sort()
    return dict(vdb)

def support(tidlist: List[Tid]) -> int:
    # liczba unikalnych sid
    return len({sid for sid, _ in tidlist})
