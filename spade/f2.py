from __future__ import annotations
from typing import Dict, List, Tuple
from .pattern import Pattern
from .join import i_join, s_join
from .vertical import Tid, support

def gen_f2(
    f1: List[Tuple[str, List[Tid], int]],
    minsup: int
) -> List[Tuple[Pattern, List[Tid], int]]:
    """
    Zwraca częste wzorce długości 2: (pattern, tidlist, sup)
    Kolejność odkrywania: najpierw I-step, potem S-step, w porządku leksykograficznym.
    """
    items = [it for (it, _, _) in f1]
    tid = {it: tl for (it, tl, _) in f1}

    out: List[Tuple[Pattern, List[Tid], int]] = []

    # I-step: <{x,y}> dla x<y
    for i in range(len(items)):
        for j in range(i+1, len(items)):
            x, y = items[i], items[j]
            tl = i_join(tid[x], tid[y])
            sup = support(tl)
            if sup >= minsup:
                pat: Pattern = ((x, y),)
                out.append((pat, tl, sup))

    # S-step: <{x}->{y}> dla wszystkich par (x,y)
    for x in items:
        for y in items:
            tl = s_join(tid[x], tid[y])
            sup = support(tl)
            if sup >= minsup:
                pat: Pattern = ((x,), (y,))
                out.append((pat, tl, sup))

    return out
