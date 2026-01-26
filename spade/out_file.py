from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Optional


OUT_COLUMNS = ["pattern_len", "num_elts", "tidlist_len", "sup", "pattern"]


@dataclass(frozen=True)
class OutMeta:
    alg: str
    input_file: str
    minsup: int
    max_elts: Optional[int] = None
    num_sequences: Optional[int] = None
    num_transactions: Optional[int] = None
    num_items: Optional[int] = None


def write_out(path: str, rows: Iterable[str], meta: Optional[OutMeta] = None) -> None:
    """
    Writes OUT file:
    - optional metadata lines starting with '#'
    - CSV header line
    - then rows (already formatted as 'len elts tidlen sup pattern' or CSV - see below)

    We will output rows as CSV (comma-separated) for consistency.
    So the caller should pass rows already in CSV order OR pass space-separated and we convert.
    """
    with open(path, "w", encoding="utf-8") as f:
        # if meta is not None:
        #     f.write(f"# alg: {meta.alg}\n")
        #     f.write(f"# input: {meta.input_file}\n")
        #     f.write(f"# minsup: {meta.minsup}\n")
        #     if meta.max_elts is not None:
        #         f.write(f"# max_elts: {meta.max_elts}\n")
        #     if meta.num_sequences is not None:
        #         f.write(f"# |D| (num_sequences): {meta.num_sequences}\n")
        #     if meta.num_transactions is not None:
        #         f.write(f"# |T| (num_transactions): {meta.num_transactions}\n")
        #     if meta.num_items is not None:
        #         f.write(f"# |I| (num_distinct_items): {meta.num_items}\n")
        #     f.write("# format: pattern_len,num_elts,tidlist_len,sup,pattern\n")

        # CSV header
        f.write(",".join(OUT_COLUMNS) + "\n")

        for line in rows:
            line = line.strip()
            if not line:
                continue

            # allow either space-separated: "len elts tid sup <{A}->{B}>"
            # or already CSV: "len,elts,tid,sup,<...>"
            if "," not in line:
                parts = line.split(" ", 4)
                if len(parts) != 5:
                    raise ValueError(f"Bad OUT row format (expected 5 fields): {line}")
                line = ",".join(parts)

            f.write(line + "\n")
