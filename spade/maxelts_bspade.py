from __future__ import annotations
from typing import Dict, List, Tuple, Callable
from collections import defaultdict

from .node import Node
from .vertical import Tid
from .pattern import Pattern
from .pattern_utils import split_last_step, pattern_sort_key
from .candidates import join_in_class
from .dspade import StatsCounter
from .f2 import gen_f2

import gc


def _group_by_prefix(nodes: List[Node]) -> Dict[Pattern, List[Node]]:
    classes: Dict[Pattern, List[Node]] = defaultdict(list)
    for n in nodes:
        pref, _, _ = split_last_step(n.pattern)
        classes[pref].append(n)

    for pref in list(classes.keys()):
        classes[pref] = sorted(classes[pref], key=lambda x: pattern_sort_key(x.pattern))

    return dict(sorted(classes.items(), key=lambda kv: pattern_sort_key(kv[0])))


def _f1_nodes_to_f2_nodes(f1_nodes: List[Node], minsup: int) -> List[Node]:
    f1_tuples: List[Tuple[str, List[Tid], int]] = []
    for n in sorted(f1_nodes, key=lambda x: x.pattern[0][0]):
        item = n.pattern[0][0]
        f1_tuples.append((item, n.tidlist, n.sup))

    f2 = gen_f2(f1_tuples, minsup)
    return [Node(pattern=p, tidlist=tl) for (p, tl, _sup) in f2]


def maxelts_bspade(
    f1_nodes: List[Node],
    item_tidlists: Dict[str, List[Tid]],
    minsup: int,
    max_elts: int,
    on_discover: Callable[[Node], None] | None = None,
    stats: StatsCounter | None = None,
) -> List[Node]:
    discovered: List[Node] = []

    # F1 (filter by max_elts)
    for n in sorted(f1_nodes, key=lambda x: pattern_sort_key(x.pattern)):
        if n.elts > max_elts:
            continue
        if stats:
            stats.add_candidate(n)
        discovered.append(n)
        if on_discover:
            on_discover(n)
        if stats:
            stats.add_discovered(n)

    # F2 (filter by max_elts)
    f2_nodes_all = _f1_nodes_to_f2_nodes(f1_nodes, minsup)
    f2_nodes = [n for n in f2_nodes_all if n.elts <= max_elts]

    for n in sorted(f2_nodes, key=lambda x: pattern_sort_key(x.pattern)):
        if stats:
            stats.add_candidate(n)
        discovered.append(n)
        if on_discover:
            on_discover(n)
        if stats:
            stats.add_discovered(n)

    current_classes = _group_by_prefix(f2_nodes)

    while current_classes:
        next_level_nodes: List[Node] = []

        for _pref, cls_nodes in current_classes.items():
            for i in range(len(cls_nodes)):
                for j in range(i + 1, len(cls_nodes)):
                    cand = join_in_class(cls_nodes[i], cls_nodes[j], minsup, stats=stats)
                    # filter max_elts
                    cand = [c for c in cand if c.elts <= max_elts]
                    if stats:
                        for c in cand:
                            stats.add_candidate(c)
                    next_level_nodes.extend(cand)

        if not next_level_nodes:
            break

        next_level_nodes = sorted(next_level_nodes, key=lambda x: pattern_sort_key(x.pattern))
        uniq = {}
        for n in next_level_nodes:
            if n.pattern not in uniq:
                uniq[n.pattern] = n
        next_level_nodes = [uniq[p] for p in sorted(uniq.keys(), key=pattern_sort_key)]

        for n in next_level_nodes:
            discovered.append(n)
            if on_discover:
                on_discover(n)
            if stats:
                stats.add_discovered(n)

        if stats is not None and getattr(stats, "gc_enabled", False):
            gc.collect()

        current_classes = _group_by_prefix(next_level_nodes)

    return discovered
