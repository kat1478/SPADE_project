from __future__ import annotations
from typing import Dict, List, Tuple, Callable
from collections import defaultdict

from .node import Node
from .vertical import Tid
from .pattern import Pattern
from .pattern_utils import split_last_step, pattern_sort_key
from .candidates import join_in_class
from .f2 import gen_f2


class StatsCounter:
    def __init__(self):
        self.candidates_by_len = {}
        self.discovered_by_len = {}
        self.sum_sup_cand = {}
        self.sum_tid_cand = {}
        self.sum_sup_disc = {}
        self.sum_tid_disc = {}

        self.max_candidate_len = 0
        self.max_discovered_len = 0

    def _inc(self, d, k, v=1):
        d[k] = d.get(k, 0) + v

    def add_candidate(self, node: Node):
        k = node.length
        if k > self.max_candidate_len:
            self.max_candidate_len = k
        self._inc(self.candidates_by_len, k, 1)
        self._inc(self.sum_sup_cand, k, node.sup)
        self._inc(self.sum_tid_cand, k, node.len_tidlist)

    def add_discovered(self, node: Node):
        k = node.length
        if k > self.max_discovered_len:
            self.max_discovered_len = k
        self._inc(self.discovered_by_len, k, 1)
        self._inc(self.sum_sup_disc, k, node.sup)
        self._inc(self.sum_tid_disc, k, node.len_tidlist)

    def total_candidates(self) -> int:
        return sum(self.candidates_by_len.values())

    def total_discovered(self) -> int:
        return sum(self.discovered_by_len.values())

    def total_sum_sup_candidates(self) -> int:
        return sum(self.sum_sup_cand.values())

    def total_sum_tid_candidates(self) -> int:
        return sum(self.sum_tid_cand.values())

    def total_sum_sup_discovered(self) -> int:
        return sum(self.sum_sup_disc.values())

    def total_sum_tid_discovered(self) -> int:
        return sum(self.sum_tid_disc.values())


def _group_by_prefix(nodes: List[Node]) -> Dict[Pattern, List[Node]]:
    classes: Dict[Pattern, List[Node]] = defaultdict(list)
    for n in nodes:
        pref, _, _ = split_last_step(n.pattern)
        classes[pref].append(n)

    # deterministic sorting inside each class
    for pref in list(classes.keys()):
        classes[pref] = sorted(classes[pref], key=lambda x: pattern_sort_key(x.pattern))

    # deterministic order of classes
    return dict(sorted(classes.items(), key=lambda kv: pattern_sort_key(kv[0])))


def _f1_nodes_to_f2_nodes(f1_nodes: List[Node], minsup: int) -> List[Node]:
    # convert Node((item,), tidlist) to tuples expected by gen_f2
    f1_tuples: List[Tuple[str, List[Tid], int]] = []
    for n in sorted(f1_nodes, key=lambda x: x.pattern[0][0]):
        item = n.pattern[0][0]
        f1_tuples.append((item, n.tidlist, n.sup))

    f2 = gen_f2(f1_tuples, minsup)
    return [Node(pattern=p, tidlist=tl) for (p, tl, _sup) in f2]


def dspade(
    f1_nodes: List[Node],
    item_tidlists: Dict[str, List[Tid]],
    minsup: int,
    on_discover: Callable[[Node], None] | None = None,
    stats: StatsCounter | None = None,
) -> List[Node]:
    """
    SPADE-like DFS (dSPADE): depth-first over equivalence classes (prefix-based).
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

    classes = _group_by_prefix(f2_nodes)

    def recurse(class_nodes: List[Node]):
        # generate next level candidates within this class via pairwise joins
        next_level: List[Node] = []
        for i in range(len(class_nodes)):
            for j in range(i + 1, len(class_nodes)):
                cand = join_in_class(class_nodes[i], class_nodes[j], minsup)
                if stats:
                    for c in cand:
                        stats.add_candidate(c)
                next_level.extend(cand)

        if not next_level:
            return

        # discover next_level nodes (they are frequent by construction)
        for n in sorted(next_level, key=lambda x: pattern_sort_key(x.pattern)):
            discovered.append(n)
            if on_discover:
                on_discover(n)
            if stats:
                stats.add_discovered(n)

        # recurse into sub-classes
        sub = _group_by_prefix(next_level)
        for _pref, sub_nodes in sub.items():
            recurse(sub_nodes)

    for _pref, cls in classes.items():
        recurse(cls)

    return discovered
