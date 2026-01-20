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
def parse_stat_file(path: Path) -> dict:
    """
    Parses a STAT_*.txt produced by run_and_stat/run_grid scripts.
    Expected format: "key: value" per line.
    """
    d = {"path": str(path)}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        d[k] = v

    # ints
    for k in [
        "sup", "maxElts",
        "total_candidates", "total_discovered",
        "max_discovered_length", "max_candidate_length",
        "num_sequences_D", "num_transactions_T", "num_distinct_items_I"
    ]:
        if k in d:
            try:
                d[k] = int(d[k])
            except ValueError:
                pass

    # floats
    for k in [
        "time_read_s", "time_mine_s", "time_write_s",
        "total_time_minus_read_s", "total_time_s",
        "tx_per_seq_mean", "tx_per_seq_std",
        "items_per_tx_mean", "items_per_tx_std"
    ]:
        if k in d:
            try:
                d[k] = float(d[k])
            except ValueError:
                pass

    return d


def load_stats(folder: str) -> list[dict]:
    files = sorted(Path(folder).glob("STAT_*.txt"))
    return [parse_stat_file(f) for f in files]


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

    if alg == "dspade":
        return "dSPADE (DFS)"
    if alg == "bspade":
        return "bSPADE (BFS)"
    if alg == "maxelts-dspade":
        return f"maxElts-dSPADE (DFS, e={me})"
    if alg == "maxelts-bspade":
        return f"maxElts-bSPADE (BFS, e={me})"
    return alg


def plot_time_vs_sup(rows, out_png: Path, title: str):
    series = {}
    for r in rows:
        key = _series_key(r)
        series.setdefault(key, []).append(r)

    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)

    for key, rr in series.items():
        rr = sorted(rr, key=lambda x: x["sup"])
        xs = [x["sup"] for x in rr]
        ys = [x["time_mine_s"] for x in rr]
        ax.plot(xs, ys, marker="o", linewidth=2.2, markersize=5, label=key)

    ax.set_title(title)
    ax.set_xlabel("Minimum support (sup) [#sequences]")
    ax.set_ylabel("Mining time [s]")
    _beautify(ax)

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)


def plot_discovered_vs_sup(rows, out_png: Path, title: str):
    series = {}
    for r in rows:
        key = _series_key(r)
        series.setdefault(key, []).append(r)

    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)

    for key, rr in series.items():
        rr = sorted(rr, key=lambda x: x["sup"])
        xs = [x["sup"] for x in rr]
        ys = [x["total_discovered"] for x in rr]
        ax.plot(xs, ys, marker="o", linewidth=2.2, markersize=5, label=key)

    ax.set_title(title)
    ax.set_xlabel("Minimum support (sup) [#sequences]")
    ax.set_ylabel("Number of discovered patterns")
    _beautify(ax)

    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)


def plot_maxelts_bar(rows_e2, rows_e3, out_png: Path, title: str, metric: str = "time_mine_s"):
    order = ["maxelts-dspade", "maxelts-bspade"]
    pretty = {
        "maxelts-dspade": "maxElts-dSPADE (DFS)",
        "maxelts-bspade": "maxElts-bSPADE (BFS)"
    }

    def get(rows, alg):
        r = [x for x in rows if x.get("alg") == alg]
        return r[0].get(metric) if r else None

    y2 = [get(rows_e2, a) for a in order]
    y3 = [get(rows_e3, a) for a in order]

    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
    x = range(len(order))
    w = 0.35

    b1 = ax.bar([i - w/2 for i in x], y2, width=w, label="maxElts = 2")
    b2 = ax.bar([i + w/2 for i in x], y3, width=w, label="maxElts = 3")

    ax.set_title(title)
    ax.set_xticks(list(x), [pretty[a] for a in order])
    ax.set_ylabel("Mining time [s]" if metric == "time_mine_s" else metric)
    _beautify(ax)

    # values above bars
    for bars in [b1, b2]:
        for bar in bars:
            h = bar.get_height()
            if h is None:
                continue
            ax.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.2f}",
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

    # Adjust these if your folders differ:
    msnbc_e2_folder = "results_msnbc_1"     # contains base + maxElts e=2 runs
    msnbc_e3_folder = "results_msnbc"       # contains maxElts e=3 runs

    msnbc_e2 = load_stats(msnbc_e2_folder)
    msnbc_e3 = load_stats(msnbc_e3_folder)

    print(f"Found {len(msnbc_e2)} STAT files in {msnbc_e2_folder}")
    print(f"Found {len(msnbc_e3)} STAT files in {msnbc_e3_folder}")

    # For the line plots: show base (dspade/bspade) + maxElts-* with e=2 only
    msnbc_for_lines = [r for r in msnbc_e2 if (r.get("maxElts") in (None, 2))]

    plot_time_vs_sup(
        msnbc_for_lines,
        outdir / "msnbc_time_vs_sup.png",
        "MSNBC: Mining time vs minimum support",
    )

    plot_discovered_vs_sup(
        msnbc_for_lines,
        outdir / "msnbc_discovered_vs_sup.png",
        "MSNBC: Number of discovered patterns vs minimum support",
    )

    # Bar chart: maxElts effect at a fixed support on MSNBC
    sup_fixed = 200000
    msnbc_fixed_e2 = filter_rows(msnbc_e2, sups={sup_fixed}, maxElts=2)
    msnbc_fixed_e3 = filter_rows(msnbc_e3, sups={sup_fixed}, maxElts=3)

    # keep only maxElts-* (not base)
    msnbc_fixed_e2 = [r for r in msnbc_fixed_e2 if "maxelts" in r.get("alg", "")]
    msnbc_fixed_e3 = [r for r in msnbc_fixed_e3 if "maxelts" in r.get("alg", "")]

    if len(msnbc_fixed_e2) >= 2 and len(msnbc_fixed_e3) >= 2:
        plot_maxelts_bar(
            msnbc_fixed_e2, msnbc_fixed_e3,
            outdir / "msnbc_maxelts_effect.png",
            f"MSNBC: Effect of maxElts at sup={sup_fixed}",
            metric="time_mine_s"
        )
    else:
        print("WARNING: Not enough maxElts data for the bar chart at sup=", sup_fixed)
        print("e2 rows:", [r.get("path") for r in msnbc_fixed_e2])
        print("e3 rows:", [r.get("path") for r in msnbc_fixed_e3])

    print("Done. PNG files in:", outdir.resolve())


if __name__ == "__main__":
    main()
