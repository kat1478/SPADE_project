from __future__ import annotations
from typing import Tuple, Literal
from .pattern import Pattern, Event, format_pattern

StepType = Literal["I", "S"]


def split_last_step(p: Pattern) -> Tuple[Pattern, StepType, str]:
    """
    SPADE equivalence-class key:
    returns (prefix, step_type, atom_item)

    Assumption consistent with your construction:
    - events are sorted tuples
    - I-extension always adds an item > last item in last event,
      so the added atom is the LAST element of the last event.
    """
    last_ev = p[-1]
    if len(last_ev) > 1:
        # I-step: prefix has same number of events, but last event without the atom (last item)
        atom = last_ev[-1]
        prefix = p[:-1] + (last_ev[:-1],)
        return prefix, "I", atom
    else:
        # S-step: prefix is pattern without last event
        atom = last_ev[0]
        prefix = p[:-1]
        return prefix, "S", atom


def pattern_sort_key(p: Pattern) -> str:
    # Deterministic ordering for classes/nodes
    return format_pattern(p)
