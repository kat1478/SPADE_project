from __future__ import annotations
from typing import Dict, List, Tuple, Any
from .pattern import Pattern
from .join import i_join, s_join
from .vertical import Tid, support

def gen_f2(
    f1: List[Tuple[str, List[Tid], int]],
    minsup: int,
    stats: Any | None = None
) -> List[Tuple[Pattern, List[Tid], int]]:
    """
    Returns frequent length-2 patterns: (pattern, tidlist, sup). 
    """
    items = [it for (it, _, _) in f1]
    tid = {it: tl for (it, tl, _) in f1}

    out: List[Tuple[Pattern, List[Tid], int]] = []

    # I-step: <{x,y}>
    for i in range(len(items)):
        for j in range(i+1, len(items)):
            x, y = items[i], items[j]
            tl = i_join(tid[x], tid[y])
            
            if stats is not None:
                # Wzorzec <{x,y}> ma 1 zdarzenie (length=1)
                stats.add_attempted(1, len(tl))

            sup = support(tl)
            if sup >= minsup:
                pat: Pattern = ((x, y),)
                out.append((pat, tl, sup))

    # S-step: <{x}->{y}>
    for x in items:
        for y in items:
            tl = s_join(tid[x], tid[y])
            
            if stats is not None:
                # Wzorzec <{x}->{y}> ma 2 zdarzenia (length=2)
                stats.add_attempted(2, len(tl))

            sup = support(tl)
            if sup >= minsup:
                pat: Pattern = ((x,), (y,))
                out.append((pat, tl, sup))

    return out