from __future__ import annotations
from typing import Dict, List, Tuple
from .vertical import VerticalDB, support, Tid

def frequent_items(vdb: VerticalDB, minsup: int) -> List[Tuple[str, List[Tid], int]]:
    """
    Zwraca listę: (item, tidlist, sup) posortowaną alfabetycznie po item,
    żeby wynik był deterministyczny.
    """
    out = []
    for it in sorted(vdb.keys()):
        tl = vdb[it]
        sup = support(tl)
        if sup >= minsup:
            out.append((it, tl, sup))
    return out
