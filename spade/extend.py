from __future__ import annotations
from typing import Dict, List, Tuple
from .pattern import Pattern, Event
from .join import i_join, s_join
from .vertical import Tid, support

def last_event(p: Pattern) -> Event:
    return p[-1]

def make_i_extension(p: Pattern, item: str) -> Pattern:
    # dodaj item do ostatniego eventu (I-step)
    ev = tuple(sorted(set(last_event(p) + (item,))))
    return p[:-1] + (ev,)

def make_s_extension(p: Pattern, item: str) -> Pattern:
    # dodaj nowy event na końcu (S-step)
    return p + ((item,),)

def extend_node(
    pattern: Pattern,
    tidlist: List[Tid],
    item_tidlists: Dict[str, List[Tid]],
    minsup: int,
) -> List[Tuple[Pattern, List[Tid]]]:
    """
    Zwraca listę (new_pattern, new_tidlist) w deterministycznej kolejności:
    najpierw I-step (itemy większe leksykograficznie od ostatniego itemu last_event),
    potem S-step (wszystkie itemy leksykograficznie).
    """
    out: List[Tuple[Pattern, List[Tid]]] = []

    last_ev = last_event(pattern)
    last_max_item = last_ev[-1]  # bo event jest posortowany

    # I-step: tylko itemy > last_max_item żeby uniknąć duplikatów (AB vs BA)
    for it in sorted(item_tidlists.keys()):
        if it <= last_max_item:
            continue
        new_tl = i_join(tidlist, item_tidlists[it])
        if support(new_tl) >= minsup:
            out.append((make_i_extension(pattern, it), new_tl))

    # S-step: wszystkie itemy
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
    Jak extend_node(), ale ucina generowanie rozszerzeń, które przekroczą max_elts.
    """
    out: List[Tuple[Pattern, List[Tid]]] = []

    current_elts = sum(len(ev) for ev in pattern)
    if current_elts >= max_elts:
        return out  # już nie wolno rozszerzać

    last_ev = last_event(pattern)
    last_max_item = last_ev[-1]

    # I-step: dodanie 1 elementu
    if current_elts + 1 <= max_elts:
        for it in sorted(item_tidlists.keys()):
            if it <= last_max_item:
                continue
            new_tl = i_join(tidlist, item_tidlists[it])
            if support(new_tl) >= minsup:
                out.append((make_i_extension(pattern, it), new_tl))

    # S-step: dodanie nowego eventu z 1 elementem
    if current_elts + 1 <= max_elts:
        for it in sorted(item_tidlists.keys()):
            new_tl = s_join(tidlist, item_tidlists[it])
            if support(new_tl) >= minsup:
                out.append((make_s_extension(pattern, it), new_tl))

    return out
