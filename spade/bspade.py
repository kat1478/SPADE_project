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


def bspade(
    f1_nodes: List[Node],
    item_tidlists: Dict[str, List[Tid]],
    minsup: int,
    on_discover: Callable[[Node], None] | None = None,
    stats: StatsCounter | None = None,
) -> List[Node]:
    """
    SPADE-like BFS (bSPADE): level-wise over equivalence classes.
    API unchanged: takes f1_nodes + item_tidlists, but internally uses SPADE joins.
    """
    discovered: List[Node] = []

    # record F1
    for n in sorted(f1_nodes, key=lambda x: pattern_sort_key(x.pattern)):
        if stats:
            stats.add_candidate(n)
        discovered.append(n)
        if on_discover:
            on_discover(n)
        if stats:
            stats.add_discovered(n)

    # build & record F2
    f2_nodes = _f1_nodes_to_f2_nodes(f1_nodes, minsup)
    for n in sorted(f2_nodes, key=lambda x: pattern_sort_key(x.pattern)):
        if stats:
            stats.add_candidate(n)
        discovered.append(n)
        if on_discover:
            on_discover(n)
        if stats:
            stats.add_discovered(n)

    # BFS levels: start from classes of F2
    current_classes = _group_by_prefix(f2_nodes)

    while current_classes:
        next_level_nodes: List[Node] = []

        # For each class, generate candidates by pairwise joins
        for _pref, cls_nodes in current_classes.items():
            for i in range(len(cls_nodes)):
                for j in range(i + 1, len(cls_nodes)):
                    cand = join_in_class(cls_nodes[i], cls_nodes[j], minsup, stats=stats)
                    if stats:
                        for c in cand:
                            stats.add_candidate(c)
                    next_level_nodes.extend(cand)

        if not next_level_nodes:
            break

        # discover all nodes on this level
        next_level_nodes = sorted(next_level_nodes, key=lambda x: pattern_sort_key(x.pattern))
        # optional dedup by pattern across classes
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

        # GC checkpoint: end of BFS level
        if stats is not None and getattr(stats, "gc_enabled", False):
            gc.collect()

        # group to next classes
        current_classes = _group_by_prefix(next_level_nodes)

    return discovered
