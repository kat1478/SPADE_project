from __future__ import annotations
from collections import defaultdict
from bisect import bisect_left
from typing import Dict, List, Tuple

Tid = Tuple[int, int]  # (sid, eid)

def index_by_sid(tidlist: List[Tid]) -> Dict[int, List[int]]:
    by = defaultdict(list)
    for sid, eid in tidlist:
        by[sid].append(eid)
    for sid in by:
        by[sid].sort()
    return dict(by)

def i_join(t1: List[Tid], t2: List[Tid]) -> List[Tid]:
    """
    I-step: same event => intersection of pairs (sid,eid)
    """
    s = set(t1)
    out = [x for x in t2 if x in s]
    out.sort()
    return out

def s_join(t1: List[Tid], t2: List[Tid]) -> List[Tid]:
    """
    S-step: new event after old one.
    Returns (sid, eid2) such that there exists an eid1 from t1 for the same sid and eid1 < eid2.
    """
    by1 = index_by_sid(t1)
    out: List[Tid] = []

    # iterate through t2 in ascending order
    for sid, eid2 in sorted(t2):
        eids1 = by1.get(sid)
        if not eids1:
            continue
        # does there exist eid1 < eid2?
        pos = bisect_left(eids1, eid2)
        if pos > 0:
            out.append((sid, eid2))

    return out
