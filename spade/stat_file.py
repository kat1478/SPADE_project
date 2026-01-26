from __future__ import annotations
from dataclasses import asdict
from typing import Optional, Dict
from spade.stats import InputStats
from spade.dspade import StatsCounter

def _fmt_float(x: float) -> str:
    return f"{x:.6f}"

def write_stat(
    path: str,
    input_stats: InputStats,
    alg_name: str,
    sup: int,
    max_elts: Optional[int],
    time_read_s: float,
    time_mine_s: float,
    time_write_s: float,
    total_time_s: float,
    stats_counter: StatsCounter,
) -> None:
    # total time minus read time
    total_minus_read = total_time_s - time_read_s

    lines = []
    # --- input stats
    lines.append(f"input_file: {input_stats.filename}")
    lines.append(f"num_sequences_D: {input_stats.num_sequences}")
    lines.append(f"num_transactions_T: {input_stats.num_transactions}")
    lines.append(f"num_distinct_items_I: {input_stats.num_distinct_items}")

    lines.append(f"tx_per_seq_min: {input_stats.min_tx_per_seq}")
    lines.append(f"tx_per_seq_max: {input_stats.max_tx_per_seq}")
    lines.append(f"tx_per_seq_mean: {_fmt_float(input_stats.mean_tx_per_seq)}")
    lines.append(f"tx_per_seq_std: {_fmt_float(input_stats.std_tx_per_seq)}")

    lines.append(f"items_per_tx_min: {input_stats.min_items_per_tx}")
    lines.append(f"items_per_tx_max: {input_stats.max_items_per_tx}")
    lines.append(f"items_per_tx_mean: {_fmt_float(input_stats.mean_items_per_tx)}")
    lines.append(f"items_per_tx_std: {_fmt_float(input_stats.std_items_per_tx)}")

    # --- parameters
    lines.append(f"alg: {alg_name}")
    lines.append(f"sup: {sup}")
    if max_elts is not None:
        lines.append(f"maxElts: {max_elts}")

    # --- timings
    lines.append(f"time_read_s: {_fmt_float(time_read_s)}")
    lines.append(f"time_mine_s: {_fmt_float(time_mine_s)}")
    lines.append(f"time_write_s: {_fmt_float(time_write_s)}")
    lines.append(f"total_time_minus_read_s: {_fmt_float(total_minus_read)}")
    lines.append(f"total_time_s: {_fmt_float(total_time_s)}")

    # --- max lengths
    lines.append(f"max_candidate_length: {stats_counter.max_candidate_len}")
    lines.append(f"max_discovered_length: {stats_counter.max_discovered_len}")

    # --- summary counters
    lines.append(f"total_candidates: {stats_counter.total_candidates()}")
    lines.append(f"total_candidates_sum_sup: {stats_counter.total_sum_sup_candidates()}")
    lines.append(f"total_candidates_sum_tidlist_len: {stats_counter.total_sum_tid_candidates()}")

    lines.append(f"total_discovered: {stats_counter.total_discovered()}")
    lines.append(f"total_discovered_sum_sup: {stats_counter.total_sum_sup_discovered()}")
    lines.append(f"total_discovered_sum_tidlist_len: {stats_counter.total_sum_tid_discovered()}")

    # --- attempted candidates (before minsup filtering)
    lines.append(f"total_attempted_candidates: {stats_counter.total_attempted()}")
    lines.append(f"total_attempted_sum_tidlist_len: {stats_counter.total_sum_tid_attempted()}")


    # --- per length 1..max_discovered_len (+1 for candidates of length L+1)
    L = stats_counter.max_discovered_len
    for k in range(1, L + 2):
        cand = stats_counter.candidates_by_len.get(k, 0)
        cand_sup = stats_counter.sum_sup_cand.get(k, 0)
        cand_tid = stats_counter.sum_tid_cand.get(k, 0)

        disc = stats_counter.discovered_by_len.get(k, 0)
        disc_sup = stats_counter.sum_sup_disc.get(k, 0)
        disc_tid = stats_counter.sum_tid_disc.get(k, 0)

        lines.append(f"candidates_len_{k}: {cand}")
        lines.append(f"candidates_len_{k}_sum_sup: {cand_sup}")
        lines.append(f"candidates_len_{k}_sum_tidlist_len: {cand_tid}")

        # discovered patterns only up to L (k=L+1 may be 0, but doesn't matter)
        lines.append(f"discovered_len_{k}: {disc}")
        lines.append(f"discovered_len_{k}_sum_sup: {disc_sup}")
        lines.append(f"discovered_len_{k}_sum_tidlist_len: {disc_tid}")

        att = stats_counter.attempted_by_len.get(k, 0)
        att_tid = stats_counter.sum_tid_attempted.get(k, 0)
        lines.append(f"attempted_len_{k}: {att}")
        lines.append(f"attempted_len_{k}_sum_tidlist_len: {att_tid}")


    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
