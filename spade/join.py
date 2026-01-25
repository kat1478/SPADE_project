from __future__ import annotations
from typing import List, Tuple

Tid = Tuple[int, int]  # (sid, eid)


def i_join(t1: List[Tid], t2: List[Tid]) -> List[Tid]:
    """
    I-step (E-join): same event => intersection on (sid,eid).
    Both lists are assumed to be sortable; we do a merge-intersection (no set).
    """
    a = sorted(t1)
    b = sorted(t2)
    i = j = 0
    out: List[Tid] = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i])
            i += 1
            j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return out


def s_join(t1: List[Tid], t2: List[Tid]) -> List[Tid]:
    """
    S-step (temporal join): new event after old one.
    Returns (sid, eid2) such that exists eid1 in t1 for same sid with eid1 < eid2.

    Implementation: streaming by sid (no dict/sid-index build).
    Assumes nothing besides sortability.
    """
    a = sorted(t1)  # (sid,eid1)
    b = sorted(t2)  # (sid,eid2)

    out: List[Tid] = []
    i = j = 0

    while i < len(a) and j < len(b):
        sid1, eid1 = a[i]
        sid2, eid2 = b[j]

        if sid1 < sid2:
            # advance in a to catch up sid
            i += 1
            continue
        if sid2 < sid1:
            # advance in b to catch up sid
            j += 1
            continue

        # same sid: collect all eid1 for this sid and all eid2 for this sid
        sid = sid1

        # get minimal eid1 in this sid (if there are multiple, any smaller works for condition eid1 < eid2)
        min_eid1 = eid1
        i += 1
        while i < len(a) and a[i][0] == sid:
            if a[i][1] < min_eid1:
                min_eid1 = a[i][1]
            i += 1

        # now process all eid2 for this sid
        while j < len(b) and b[j][0] == sid:
            if b[j][1] > min_eid1:
                out.append(b[j])
            j += 1

    return out
