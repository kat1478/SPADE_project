from __future__ import annotations
import argparse
from spade.io import read_csv
from spade.vertical import build_vertical_db
from spade.f1 import frequent_items
from spade.node import Node
from spade.maxelts_bspade import maxelts_bspade
from spade.dspade import StatsCounter
from spade.pattern import format_pattern

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--sup", required=True, type=int)
    ap.add_argument("--maxElts", required=True, type=int)
    ap.add_argument("--out", required=False)
    args = ap.parse_args()

    records = read_csv(args.input)
    vdb = build_vertical_db(records)
    f1 = frequent_items(vdb, minsup=args.sup)

    item_tidlists = {it: tl for (it, tl, _) in f1}
    f1_nodes = [Node(pattern=((it,),), tidlist=tl) for (it, tl, _) in f1]

    stats = StatsCounter()
    lines = []

    def on_discover(n: Node):
        lines.append(f"{n.length} {n.elts} {n.len_tidlist} {n.sup} {format_pattern(n.pattern)}")

    maxelts_bspade(f1_nodes, item_tidlists, minsup=args.sup, max_elts=args.maxElts,
                   on_discover=on_discover, stats=stats)

    text = "\n".join(lines)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)

if __name__ == "__main__":
    main()
