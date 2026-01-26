from __future__ import annotations
from typing import List, Dict
from .node import Node
from .pattern import Pattern
from .pattern_utils import split_last_step, pattern_sort_key
from .join import i_join, s_join


def join_in_class(a: Node, b: Node, minsup: int, stats=None) -> List[Node]:
    """
    Join two nodes that MUST belong to the same equivalence class (same prefix).
    Generates (k+1)-candidates according to SPADE cases:
      I+I -> I
      I+S -> S
      S+S -> {event, seq_ab, seq_ba}
    """
    pa, ta, xa = split_last_step(a.pattern)
    pb, tb, xb = split_last_step(b.pattern)
    if pa != pb:
        return []

    out: List[Node] = []

    def emit(pat: Pattern, tl):
        # attempted candidate (before minsup)
        if stats is not None:
            # length is number of events in pattern
            k = len(pat)
            stats.add_attempted(k, len(tl))

        # avoid extra work: compute sup via Node.sup property
        n = Node(pattern=pat, tidlist=tl)
        if n.sup >= minsup:
            out.append(n)

    # I + I -> I (event atom)
    if ta == "I" and tb == "I":
        # candidate is union in the last event (deterministic sorted set)
        last_ev = a.pattern[-1]
        new_ev = tuple(sorted(set(last_ev + (xb,))))
        pat = a.pattern[:-1] + (new_ev,)
        tl = i_join(a.tidlist, b.tidlist)
        emit(pat, tl)

    # I + S -> S
    elif ta == "I" and tb == "S":
        pat = a.pattern + ((xb,),)
        tl = s_join(a.tidlist, b.tidlist)
        emit(pat, tl)

    elif ta == "S" and tb == "I":
        pat = b.pattern + ((xa,),)
        tl = s_join(b.tidlist, a.tidlist)
        emit(pat, tl)

    # S + S -> 3 candidates
    else:
        # event: prefix -> (xa xb)
        ev = tuple(sorted((xa, xb)))
        pat_event = pa + (ev,)
        tl_event = i_join(a.tidlist, b.tidlist)
        emit(pat_event, tl_event)

        # seq: prefix -> xa -> xb
        pat_ab = a.pattern + ((xb,),)
        tl_ab = s_join(a.tidlist, b.tidlist)
        emit(pat_ab, tl_ab)

        # seq: prefix -> xb -> xa
        pat_ba = b.pattern + ((xa,),)
        tl_ba = s_join(b.tidlist, a.tidlist)
        emit(pat_ba, tl_ba)

    # Deduplicate by pattern (can happen from different pairs)
    unique: Dict[Pattern, Node] = {}
    for n in out:
        if n.pattern not in unique:
            unique[n.pattern] = n

    return [unique[p] for p in sorted(unique.keys(), key=pattern_sort_key)]
