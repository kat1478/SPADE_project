from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass(frozen=True)
class DataInfo:
    fname: str
    D: int   # num sequences
    T: int   # num transactions/events
    I: int   # num distinct items

def dataset_info(input_path: str, D: int, T: int, I: int) -> DataInfo:
    p = Path(input_path)
    # bierzemy nazwę bez rozszerzenia
    fname = p.stem
    return DataInfo(fname=fname, D=D, T=T, I=I)

def build_out_name(alg: str, info: DataInfo, sup: int, max_elts: Optional[int]) -> str:
    # alg w stylu: dspade, bspade, maxelts-dspade, maxelts-bspade
    base = f"OUT_{alg}_{info.fname}_d{info.D}_t{info.T}_i{info.I}_s{sup}"
    if max_elts is not None:
        base += f"_e{max_elts}"
    return base + ".txt"

def build_stat_name(alg: str, info: DataInfo, sup: int, max_elts: Optional[int]) -> str:
    base = f"STAT_{alg}_{info.fname}_d{info.D}_t{info.T}_i{info.I}_s{sup}"
    if max_elts is not None:
        base += f"_e{max_elts}"
    return base + ".txt"
