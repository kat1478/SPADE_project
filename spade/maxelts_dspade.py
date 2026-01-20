from __future__ import annotations
from typing import Dict, List, Callable
from .node import Node
from .extend import extend_node_maxelts
from .vertical import Tid
from .dspade import StatsCounter

def maxelts_dspade(
    f1_nodes: List[Node],
    item_tidlists: Dict[str, List[Tid]],
    minsup: int,
    max_elts: int,
    on_discover: Callable[[Node], None] | None = None,
    stats: StatsCounter | None = None,
) -> List[Node]:
    discovered: List[Node] = []

    def dfs(node: Node):
        discovered.append(node)
        if on_discover:
            on_discover(node)
        if stats:
            stats.add_discovered(node)

        # cutoff is handled in extend_node_maxelts
        extensions = extend_node_maxelts(node.pattern, node.tidlist, item_tidlists, minsup, max_elts)
        for p2, tl2 in extensions:
            child = Node(pattern=p2, tidlist=tl2)
            if stats:
                stats.add_candidate(child)
            dfs(child)

    for n in f1_nodes:
        if stats:
            stats.add_candidate(n)
        # if f1 already exceeds max_elts (e.g., max_elts=0), skip it
        if n.elts <= max_elts:
            dfs(n)

    return discovered
