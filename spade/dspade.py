from __future__ import annotations
from typing import Dict, List, Tuple, Callable
from .node import Node
from .pattern import format_pattern
from .extend import extend_node
from .vertical import Tid

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

    # pomocnicze sumy globalne
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


def dspade(
    f1_nodes: List[Node],
    item_tidlists: Dict[str, List[Tid]],
    minsup: int,
    on_discover: Callable[[Node], None] | None = None,
    stats: StatsCounter | None = None,
) -> List[Node]:
    """
    DFS enumeration. Zwraca listę odkrytych wzorców w kolejności odkrywania.
    """
    discovered: List[Node] = []

    def dfs(node: Node):
        # odkryty wzorzec (częsty) — zapisujemy
        discovered.append(node)
        if on_discover:
            on_discover(node)
        if stats:
            stats.add_discovered(node)

        # generuj rozszerzenia
        extensions = extend_node(node.pattern, node.tidlist, item_tidlists, minsup)
        for (p2, tl2) in extensions:
            child = Node(pattern=p2, tidlist=tl2)
            if stats:
                stats.add_candidate(child)
            dfs(child)

    # Start DFS z każdym częstym 1-wzorcem
    for n in f1_nodes:
        if stats:
            stats.add_candidate(n)  # kandydat długości 1 też liczmy jako utworzony
        dfs(n)

    return discovered
