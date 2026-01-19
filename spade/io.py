from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, List, Tuple
import csv

Item = str
Sid = int
Eid = int

@dataclass(frozen=True)
class Record:
    sid: Sid
    eid: Eid
    items: Tuple[Item, ...]  # unique, sorted


def read_csv(path: str) -> List[Record]:
    records: List[Record] = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = int(row["sid"])
            eid = int(row["eid"])
            raw_items = row["items"].strip()
            if not raw_items:
                raise ValueError(f"Empty items in row: {row}")
            items = tuple(sorted(set(raw_items.split())))
            records.append(Record(sid=sid, eid=eid, items=items))

    records.sort(key=lambda r: (r.sid, r.eid))
    validate(records)
    return records


def validate(records: Iterable[Record]) -> None:
    last_eid_by_sid: dict[Sid, Eid] = {}
    for r in records:
        if len(r.items) == 0:
            raise ValueError(f"Empty items for (sid={r.sid}, eid={r.eid})")

        # eid strictly increasing within sid
        if r.sid in last_eid_by_sid:
            if r.eid <= last_eid_by_sid[r.sid]:
                raise ValueError(
                    f"Non-increasing eid for sid={r.sid}: "
                    f"{last_eid_by_sid[r.sid]} -> {r.eid}"
                )
        last_eid_by_sid[r.sid] = r.eid

        # items uniqueness enforced by read_csv, but keep a safety check
        if len(set(r.items)) != len(r.items):
            raise ValueError(f"Duplicate items for (sid={r.sid}, eid={r.eid}): {r.items}")


def read_spmf(path: str) -> List[Record]:
    """
    SPMF sequential format:
    - items are integers (we keep them as strings)
    - -1 ends an event
    - -2 ends a sequence
    Each line may contain one or more sequences; we treat each line as one sid if it ends with -2.
    """
    records: List[Record] = []
    sid = 1

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            tokens = line.split()

            current_event = []
            eid = 1
            had_any = False

            for tok in tokens:
                if tok == "-1":
                    if current_event:
                        items = tuple(sorted(set(current_event)))
                        records.append(Record(sid=sid, eid=eid, items=items))
                        eid += 1
                        current_event = []
                        had_any = True
                elif tok == "-2":
                    # end sequence
                    if current_event:
                        items = tuple(sorted(set(current_event)))
                        records.append(Record(sid=sid, eid=eid, items=items))
                        current_event = []
                        had_any = True
                    if had_any:
                        sid += 1
                    eid = 1
                    had_any = False
                else:
                    # item
                    current_event.append(tok)

    records.sort(key=lambda r: (r.sid, r.eid))
    validate(records)
    return records
