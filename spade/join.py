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
    I-step: ten sam event => przecięcie par (sid,eid)
    """
    s = set(t1)
    out = [x for x in t2 if x in s]
    out.sort()
    return out

def s_join(t1: List[Tid], t2: List[Tid]) -> List[Tid]:
    """
    S-step: nowy event po starym.
    Zwracamy (sid, eid2) takie, że istnieje eid1 z t1 dla tego sid i eid1 < eid2.
    """
    by1 = index_by_sid(t1)
    out: List[Tid] = []

    # iterujemy po t2 w kolejności rosnącej
    for sid, eid2 in sorted(t2):
        eids1 = by1.get(sid)
        if not eids1:
            continue
        # czy istnieje eid1 < eid2?
        pos = bisect_left(eids1, eid2)
        if pos > 0:
            out.append((sid, eid2))

    return out
