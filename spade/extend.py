from __future__ import annotations
from typing import Dict, List, Tuple
from .pattern import Pattern, Event
from .join import i_join, s_join
from .vertical import Tid, support

def last_event(p: Pattern) -> Event:
    return p[-1]

def make_i_extension(p: Pattern, item: str) -> Pattern:
    # add item to the last event (I-step)
    ev = tuple(sorted(set(last_event(p) + (item,))))
    return p[:-1] + (ev,)

def make_s_extension(p: Pattern, item: str) -> Pattern:
    # add new event with item (S-step)
    return p + ((item,),)

def extend_node(
    pattern: Pattern,
    tidlist: List[Tid],
    item_tidlists: Dict[str, List[Tid]],
    minsup: int,
) -> List[Tuple[Pattern, List[Tid]]]:
    """
    Returns a list of (new_pattern, new_tidlist) in deterministic order:
    first I-steps (adding item to last event), then S-steps (adding new event with item).
    """
    out: List[Tuple[Pattern, List[Tid]]] = []

    last_ev = last_event(pattern)
    last_max_item = last_ev[-1]  # because events are sorted tuples

    # I-step: only items > last_max_item to avoid duplicates (AB vs BA)
    for it in sorted(item_tidlists.keys()):
        if it <= last_max_item:
            continue
        new_tl = i_join(tidlist, item_tidlists[it])
        if support(new_tl) >= minsup:
            out.append((make_i_extension(pattern, it), new_tl))

    # S-step: all items
    for it in sorted(item_tidlists.keys()):
        new_tl = s_join(tidlist, item_tidlists[it])
        if support(new_tl) >= minsup:
            out.append((make_s_extension(pattern, it), new_tl))

    return out


def extend_node_maxelts(
    pattern: Pattern,
    tidlist: List[Tid],
    item_tidlists: Dict[str, List[Tid]],
    minsup: int,
    max_elts: int,
) -> List[Tuple[Pattern, List[Tid]]]:
    """
    Like extend_node, but respects max_elts constraint.
    """
    out: List[Tuple[Pattern, List[Tid]]] = []

    current_elts = sum(len(ev) for ev in pattern)
    if current_elts >= max_elts:
        return out  # no extensions possible

    last_ev = last_event(pattern)
    last_max_item = last_ev[-1]

    # I-step: adding 1 element
    if current_elts + 1 <= max_elts:
        for it in sorted(item_tidlists.keys()):
            if it <= last_max_item:
                continue
            new_tl = i_join(tidlist, item_tidlists[it])
            if support(new_tl) >= minsup:
                out.append((make_i_extension(pattern, it), new_tl))

    # S-step: adding a new event with 1 element
    if current_elts + 1 <= max_elts:
        for it in sorted(item_tidlists.keys()):
            new_tl = s_join(tidlist, item_tidlists[it])
            if support(new_tl) >= minsup:
                out.append((make_s_extension(pattern, it), new_tl))

    return out
