from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
from .pattern import Pattern, pattern_len, num_elts
from .vertical import Tid, support

@dataclass(frozen=True)
class Node:
    pattern: Pattern
    tidlist: List[Tid]

    @property
    def sup(self) -> int:
        return support(self.tidlist)

    @property
    def len_tidlist(self) -> int:
        return len(self.tidlist)

    @property
    def length(self) -> int:
        return pattern_len(self.pattern)

    @property
    def elts(self) -> int:
        return num_elts(self.pattern)
