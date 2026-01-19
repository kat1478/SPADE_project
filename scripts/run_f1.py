from __future__ import annotations
import argparse
from spade.io import read_csv
from spade.vertical import build_vertical_db
from spade.f1 import frequent_items

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV: sid,eid,items")
    ap.add_argument("--sup", required=True, type=int, help="min support as count of sequences")
    ap.add_argument("--out", required=False, help="Optional OUT file path for length-1 patterns")
    args = ap.parse_args()

    records = read_csv(args.input)
    vdb = build_vertical_db(records)

    f1 = frequent_items(vdb, minsup=args.sup)

    # OUT format: length(pattern), num_elts, len(tidlist), sup, pattern
    lines = []
    for (it, tidlist, sup) in f1:
        length_pattern = 1
        num_elts = 1
        len_tidlist = len(tidlist)
        pattern_str = f"<{{{it}}}>"
        lines.append(f"{length_pattern} {num_elts} {len_tidlist} {sup} {pattern_str}")

    text = "\n".join(lines)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)

if __name__ == "__main__":
    main()
