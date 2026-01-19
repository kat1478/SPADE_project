from __future__ import annotations
from collections import deque
from typing import Dict, List, Tuple, Callable
from .node import Node
from .extend import extend_node
from .vertical import Tid

from .dspade import StatsCounter  # można współdzielić licznik

def bspade(
    f1_nodes: List[Node],
    item_tidlists: Dict[str, List[Tid]],
    minsup: int,
    on_discover: Callable[[Node], None] | None = None,
    stats: StatsCounter | None = None,
) -> List[Node]:
    """
    BFS enumeration. Zwraca listę odkrytych wzorców w kolejności odkrywania.
    """
    discovered: List[Node] = []

    q = deque()

    # start: poziom 1
    for n in f1_nodes:
        if stats:
            stats.add_candidate(n)
        q.append(n)

    while q:
        node = q.popleft()

        # odkryty (częsty) — zapisujemy
        discovered.append(node)
        if on_discover:
            on_discover(node)
        if stats:
            stats.add_discovered(node)

        # generuj dzieci i wrzuć do kolejki
        extensions = extend_node(node.pattern, node.tidlist, item_tidlists, minsup)
        for p2, tl2 in extensions:
            child = Node(pattern=p2, tidlist=tl2)
            if stats:
                stats.add_candidate(child)
            q.append(child)

    return discovered
