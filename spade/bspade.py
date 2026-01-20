from __future__ import annotations
from collections import deque
from typing import Dict, List, Tuple, Callable
from .node import Node
from .extend import extend_node
from .vertical import Tid

from .dspade import StatsCounter  

def bspade(
    f1_nodes: List[Node],
    item_tidlists: Dict[str, List[Tid]],
    minsup: int,
    on_discover: Callable[[Node], None] | None = None,
    stats: StatsCounter | None = None,
) -> List[Node]:
    """
    BFS enumeration. Returns a list of discovered patterns in the order of discovery.
    """
    discovered: List[Node] = []

    q = deque()

    # start: level 1
    for n in f1_nodes:
        if stats:
            stats.add_candidate(n)
        q.append(n)

    while q:
        node = q.popleft()

        # discovered (frequent) — record/save
        discovered.append(node)
        if on_discover:
            on_discover(node)
        if stats:
            stats.add_discovered(node)

        # generate children and push to the queue
        extensions = extend_node(node.pattern, node.tidlist, item_tidlists, minsup)
        for p2, tl2 in extensions:
            child = Node(pattern=p2, tidlist=tl2)
            if stats:
                stats.add_candidate(child)
            q.append(child)

    return discovered
