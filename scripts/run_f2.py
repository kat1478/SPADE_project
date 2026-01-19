from __future__ import annotations
import argparse
from spade.io import read_csv
from spade.vertical import build_vertical_db
from spade.f1 import frequent_items
from spade.f2 import gen_f2
from spade.pattern import pattern_len, num_elts, format_pattern

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--sup", required=True, type=int)
    ap.add_argument("--out", required=False)
    args = ap.parse_args()

    records = read_csv(args.input)
    vdb = build_vertical_db(records)

    f1 = frequent_items(vdb, minsup=args.sup)
    f2 = gen_f2(f1, minsup=args.sup)

    lines = []
    for pat, tidlist, sup in f2:
        lines.append(
            f"{pattern_len(pat)} {num_elts(pat)} {len(tidlist)} {sup} {format_pattern(pat)}"
        )

    text = "\n".join(lines)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)

if __name__ == "__main__":
    main()
