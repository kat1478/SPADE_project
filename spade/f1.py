from __future__ import annotations
from typing import Dict, List, Tuple
from .vertical import VerticalDB, support, Tid

def frequent_items(vdb: VerticalDB, minsup: int) -> List[Tuple[str, List[Tid], int]]:
    """
    Returns a list: (item, tidlist, sup) sorted alphabetically by item to ensure deterministic output.
    
    """
    out = []
    for it in sorted(vdb.keys()):
        tl = vdb[it]
        sup = support(tl)
        if sup >= minsup:
            out.append((it, tl, sup))
    return out
