from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

Event = Tuple[str, ...]
Pattern = Tuple[Event, ...]

def pattern_len(p: Pattern) -> int:
    return len(p)

def num_elts(p: Pattern) -> int:
    return sum(len(ev) for ev in p)

def format_pattern(p: Pattern) -> str:
    # OUT-friendly: <{A B}->{C}->{D E}>
    parts = []
    for ev in p:
        parts.append("{"+ " ".join(ev) +"}")
    return "<" + "->".join(parts) + ">"

