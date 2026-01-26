from __future__ import annotations
import argparse
import gc
import time
from pathlib import Path

from spade.io import read_csv, read_spmf
from spade.stats import compute_input_stats
from spade.vertical import build_vertical_db
from spade.f1 import frequent_items
from spade.node import Node
from spade.pattern import format_pattern

from spade.dspade import dspade, StatsCounter
from spade.bspade import bspade
from spade.maxelts_dspade import maxelts_dspade
from spade.maxelts_bspade import maxelts_bspade

from spade.stat_file import write_stat
from spade.naming import dataset_info, build_out_name, build_stat_name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--alg", required=True, choices=["dspade", "bspade", "maxelts-dspade", "maxelts-bspade"])
    ap.add_argument("--sup", required=True, type=int)
    ap.add_argument("--maxElts", required=False, type=int)
    ap.add_argument("--resultsDir", required=True, help="Directory for OUT/STAT files")
    ap.add_argument("--gc", action="store_true", help="Force garbage collection at checkpoints (debug)")

    args = ap.parse_args()

    results_dir = Path(args.resultsDir)
    results_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()

    # READ
    t_read0 = time.perf_counter()
    if args.input.endswith(".csv"):
        records = read_csv(args.input)
    else:
        records = read_spmf(args.input)
    input_stats = compute_input_stats(records, filename=args.input)
    t_read1 = time.perf_counter()

    info = dataset_info(
        args.input,
        input_stats.num_sequences,
        input_stats.num_transactions,
        input_stats.num_distinct_items,
    )

    # PREP
    vdb = build_vertical_db(records)
    f1 = frequent_items(vdb, minsup=args.sup)
    item_tidlists = {it: tl for (it, tl, _) in f1}  # kept for API compatibility
    f1_nodes = [Node(pattern=((it,),), tidlist=tl) for (it, tl, _) in f1]

    if args.gc:
        gc.collect()

    # Resolve names early (so we can stream OUT during mining)
    max_elts = None
    if args.alg in ("maxelts-dspade", "maxelts-bspade"):
        if args.maxElts is None:
            raise ValueError("maxElts is required for maxelts variants")
        max_elts = args.maxElts

    out_name = build_out_name(args.alg, info, sup=args.sup, max_elts=max_elts)
    stat_name = build_stat_name(args.alg, info, sup=args.sup, max_elts=max_elts)

    out_path = results_dir / out_name
    stat_path = results_dir / stat_name

    # MINE + stream OUT
    stats = StatsCounter()
    stats.gc_enabled = args.gc


    t_mine0 = time.perf_counter()
    with open(out_path, "w", encoding="utf-8") as out_f:
        # CSV header only (clean OUT)
        out_f.write("pattern_len,num_elts,tidlist_len,sup,pattern\n")

        def on_discover(n: Node):
            out_f.write(f"{n.length},{n.elts},{n.len_tidlist},{n.sup},{format_pattern(n.pattern)}\n")

        if args.alg == "dspade":
            dspade(f1_nodes, item_tidlists, minsup=args.sup, on_discover=on_discover, stats=stats)
        elif args.alg == "bspade":
            bspade(f1_nodes, item_tidlists, minsup=args.sup, on_discover=on_discover, stats=stats)
        elif args.alg == "maxelts-dspade":
            maxelts_dspade(
                f1_nodes, item_tidlists,
                minsup=args.sup,
                max_elts=max_elts,
                on_discover=on_discover,
                stats=stats,
            )
        else:  # maxelts-bspade
            maxelts_bspade(
                f1_nodes, item_tidlists,
                minsup=args.sup,
                max_elts=max_elts,
                on_discover=on_discover,
                stats=stats,
            )
    t_mine1 = time.perf_counter()

    # WRITE STAT
    t_write0 = time.perf_counter()
    total_time = time.perf_counter() - t0

    write_stat(
        path=str(stat_path),
        input_stats=input_stats,
        alg_name=args.alg,
        sup=args.sup,
        max_elts=max_elts,
        time_read_s=(t_read1 - t_read0),
        time_mine_s=(t_mine1 - t_mine0),
        time_write_s=0.0,  # we fill after measuring
        total_time_s=0.0,  # we fill after measuring
        stats_counter=stats,
    )

    t_write1 = time.perf_counter()
    total_time = time.perf_counter() - t0

    # overwrite STAT with correct write/total times
    write_stat(
        path=str(stat_path),
        input_stats=input_stats,
        alg_name=args.alg,
        sup=args.sup,
        max_elts=max_elts,
        time_read_s=(t_read1 - t_read0),
        time_mine_s=(t_mine1 - t_mine0),
        time_write_s=(t_write1 - t_write0),
        total_time_s=total_time,
        stats_counter=stats,
    )

    print(f"Wrote OUT:  {out_path}")
    print(f"Wrote STAT: {stat_path}")


if __name__ == "__main__":
    main()
