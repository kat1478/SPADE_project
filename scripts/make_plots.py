from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# ---------- Global style (report-friendly) ----------
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "legend.fontsize": 10,
})


# ---------- Parsing STAT files ----------
INT_KEYS = {
    "sup", "maxElts",
    "total_discovered",
    "total_candidates", 
    "total_attempted_candidates",
    "total_attempted_sum_tidlist_len",
    "max_discovered_length", "max_candidate_length",
    "num_sequences_D", "num_transactions_T", "num_distinct_items_I",
}

FLOAT_KEYS = {
    "time_read_s", "time_mine_s", "time_write_s",
    "total_time_minus_read_s", "total_time_s",
    "tx_per_seq_mean", "tx_per_seq_std",
    "items_per_tx_mean", "items_per_tx_std",
}


def parse_stat_file(path: Path) -> dict:
    """
    Parses a STAT_*.txt produced by run_and_stat/run_grid scripts.
    Expected format: "key: value" per line.
    """
    d = {"path": str(path)}
    text = path.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        d[k] = v

    # ints
    for k in INT_KEYS:
        if k in d:
            try:
                d[k] = int(d[k])
            except ValueError:
                pass

    # floats
    for k in FLOAT_KEYS:
        if k in d:
            try:
                d[k] = float(d[k])
            except ValueError:
                pass

    # normalize alg name (just in case)
    if "alg" in d:
        d["alg"] = d["alg"].strip()

    return d


def load_stats(folder: str) -> list[dict]:
    files = sorted(Path(folder).glob("STAT_*.txt"))
    return [parse_stat_file(f) for f in files]


def merge_stats(*folders: str) -> list[dict]:
    rows: list[dict] = []
    for fol in folders:
        rows.extend(load_stats(fol))
    return rows


def filter_rows(rows, alg=None, maxElts=None, sups=None):
    out = []
    for r in rows:
        if alg is not None and r.get("alg") != alg:
            continue
        if maxElts is not None and r.get("maxElts") != maxElts:
            continue
        if sups is not None and r.get("sup") not in sups:
            continue
        out.append(r)
    return out


# ---------- Plot helpers ----------
def _beautify(ax):
    ax.grid(True, which="major", linestyle="--", linewidth=0.7, alpha=0.6)
    ax.set_axisbelow(True)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)


def _series_key(r):
    alg = r.get("alg", "unknown")
    me = r.get("maxElts", None)

    # alg values in your codebase: dspade / bspade / maxelts-dspade / maxelts-bspade
    if alg == "dspade":
        return "dSPADE (DFS)"
    if alg == "bspade":
        return "bSPADE (BFS)"
    if alg == "maxelts-dspade":
        return f"maxElts-dSPADE (DFS, e={me})"
    if alg == "maxelts-bspade":
        return f"maxElts-bSPADE (BFS, e={me})"
    return alg


def plot_metric_vs_sup(rows, out_png: Path, title: str, metric: str, ylabel: str):
    """
    Line plot: metric vs sup for all series (alg + maxElts).
    """
    series = {}
    for r in rows:
        if metric not in r:
            continue
        key = _series_key(r)
        series.setdefault(key, []).append(r)

    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)

    for key, rr in series.items():
        rr = sorted(rr, key=lambda x: x["sup"])
        xs = [x["sup"] for x in rr]
        ys = [x.get(metric, 0) for x in rr]
        ax.plot(xs, ys, marker="o", linewidth=2.2, markersize=5, label=key)

    ax.set_title(title)
    ax.set_xlabel("Minimum support (sup) [#sequences]")
    ax.set_ylabel(ylabel)
    _beautify(ax)

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)


def plot_maxelts_bar(rows_e2, rows_e3, out_png: Path, title: str, metric: str, ylabel: str):
    """
    Bar plot: compare e=2 vs e=3 for maxElts-* algorithms at fixed sup.
    """
    order = ["maxelts-dspade", "maxelts-bspade"]
    pretty = {
        "maxelts-dspade": "maxElts-dSPADE (DFS)",
        "maxelts-bspade": "maxElts-bSPADE (BFS)",
    }

    def get(rows, alg):
        rr = [x for x in rows if x.get("alg") == alg]
        return rr[0].get(metric) if rr else None

    y2 = [get(rows_e2, a) for a in order]
    y3 = [get(rows_e3, a) for a in order]

    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
    x = range(len(order))
    w = 0.35

    b1 = ax.bar([i - w/2 for i in x], y2, width=w, label="maxElts = 2")
    b2 = ax.bar([i + w/2 for i in x], y3, width=w, label="maxElts = 3")

    ax.set_title(title)
    ax.set_xticks(list(x), [pretty[a] for a in order])
    ax.set_ylabel(ylabel)
    _beautify(ax)

    # values above bars
    for bars in [b1, b2]:
        for bar in bars:
            h = bar.get_height()
            if h is None:
                continue
            ax.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.2f}" if isinstance(h, float) else f"{h}",
                    ha="center", va="bottom", fontsize=9)

    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)


# ---------- Main ----------
def main():
    outdir = Path("plots")
    outdir.mkdir(exist_ok=True)

    print("CWD:", Path().resolve())
    print("Writing plots to:", outdir.resolve())

    
    msnbc_folders = ["results_final/msnbc", "results_final/msnbc_maxelts"]  
    bike_folders = ["results_final/bike"]
    covid_folders = ["results_final/covid"]

    # Load
    msnbc = merge_stats(*msnbc_folders)
    bike = merge_stats(*bike_folders)
    covid = merge_stats(*covid_folders)

    print(f"MSNBC rows: {len(msnbc)}")
    print(f"BIKE rows:  {len(bike)}")
    print(f"COVID rows: {len(covid)}")

    # ========== MSNBC: sup plots  ==========
    msnbc_lines = [r for r in msnbc if (r.get("maxElts") in (None, 2))]

    plot_metric_vs_sup(
        msnbc_lines,
        outdir / "msnbc_total_time_vs_sup.png",
        "MSNBC: total_time_s vs sup",
        metric="total_time_s",
        ylabel="Total time [s]",
    )

    plot_metric_vs_sup(
        msnbc_lines,
        outdir / "msnbc_discovered_vs_sup.png",
        "MSNBC: total_discovered vs sup",
        metric="total_discovered",
        ylabel="Number of discovered patterns",
    )

    plot_metric_vs_sup(
        msnbc_lines,
        outdir / "msnbc_attempted_vs_sup.png",
        "MSNBC: total_attempted_candidates vs sup",
        metric="total_attempted_candidates",
        ylabel="Attempted candidates (join trials)",
    )

    plot_metric_vs_sup(
        msnbc_lines,
        outdir / "msnbc_attempted_tid_sum_vs_sup.png",
        "MSNBC: total_attempted_sum_tidlist_len vs sup",
        metric="total_attempted_sum_tidlist_len",
        ylabel="Sum of tidlist lengths (attempted joins)",
    )

    # ========== MSNBC: maxElts effect at fixed sup ==========
    sup_fixed = 200000
    msnbc_e2 = [r for r in msnbc if r.get("maxElts") == 2 and r.get("sup") == sup_fixed]
    msnbc_e3 = [r for r in msnbc if r.get("maxElts") == 3 and r.get("sup") == sup_fixed]
    msnbc_e2 = [r for r in msnbc_e2 if "maxelts" in r.get("alg", "")]
    msnbc_e3 = [r for r in msnbc_e3 if "maxelts" in r.get("alg", "")]

    if len(msnbc_e2) >= 2 and len(msnbc_e3) >= 2:
        plot_maxelts_bar(
            msnbc_e2, msnbc_e3,
            outdir / "msnbc_maxelts_total_time.png",
            f"MSNBC: effect of maxElts at sup={sup_fixed} (total_time_s)",
            metric="total_time_s",
            ylabel="Total time [s]",
        )
        plot_maxelts_bar(
            msnbc_e2, msnbc_e3,
            outdir / "msnbc_maxelts_attempted.png",
            f"MSNBC: effect of maxElts at sup={sup_fixed} (attempted)",
            metric="total_attempted_candidates",
            ylabel="Attempted candidates (join trials)",
        )
    else:
        print("WARNING: Not enough MSNBC maxElts data for bar plots at sup=", sup_fixed)

    # ========== BIKE: sup plots (bazowe DFS vs BFS) ==========
    bike_base = [r for r in bike if r.get("alg") in ("bspade", "dspade")]

    plot_metric_vs_sup(
        bike_base,
        outdir / "bike_total_time_vs_sup.png",
        "BIKE: total_time_s vs sup (DFS vs BFS)",
        metric="total_time_s",
        ylabel="Total time [s]",
    )

    plot_metric_vs_sup(
        bike_base,
        outdir / "bike_discovered_vs_sup.png",
        "BIKE: total_discovered vs sup (DFS vs BFS)",
        metric="total_discovered",
        ylabel="Number of discovered patterns",
    )

    plot_metric_vs_sup(
        bike_base,
        outdir / "bike_attempted_vs_sup.png",
        "BIKE: total_attempted_candidates vs sup (DFS vs BFS)",
        metric="total_attempted_candidates",
        ylabel="Attempted candidates (join trials)",
    )

    plot_metric_vs_sup(
        bike_base,
        outdir / "bike_attempted_tid_sum_vs_sup.png",
        "BIKE: total_attempted_sum_tidlist_len vs sup (DFS vs BFS)",
        metric="total_attempted_sum_tidlist_len",
        ylabel="Sum of tidlist lengths (attempted joins)",
    )

    # ========== COVID: maxElts effect  ==========
    covid_maxelts = [r for r in covid if "maxelts" in r.get("alg", "")]
    sup_covid = 495
    covid_e2 = [r for r in covid_maxelts if r.get("maxElts") == 2 and r.get("sup") == sup_covid]
    covid_e3 = [r for r in covid_maxelts if r.get("maxElts") == 3 and r.get("sup") == sup_covid]

    if len(covid_e2) >= 2 and len(covid_e3) >= 2:
        plot_maxelts_bar(
            covid_e2, covid_e3,
            outdir / "covid_maxelts_total_time.png",
            f"COVID: effect of maxElts at sup={sup_covid} (total_time_s)",
            metric="total_time_s",
            ylabel="Total time [s]",
        )
        plot_maxelts_bar(
            covid_e2, covid_e3,
            outdir / "covid_maxelts_attempted.png",
            f"COVID: effect of maxElts at sup={sup_covid} (attempted)",
            metric="total_attempted_candidates",
            ylabel="Attempted candidates (join trials)",
        )
    else:
        print("WARNING: Not enough COVID maxElts data for bar plots at sup=", sup_covid)

    print("Done. PNG files in:", outdir.resolve())


if __name__ == "__main__":
    main()
