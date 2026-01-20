from __future__ import annotations
import argparse
from spade.io import read_csv, read_spmf
from spade.stats import compute_input_stats

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to CSV: sid,eid,items")
    ap.add_argument("--out", required=False, help="Output STAT file path")
    args = ap.parse_args()

    if args.input.endswith(".csv"):
        records = read_csv(args.input)
    elif args.input.endswith(".spmf") or args.input.endswith(".spm"):
        records = read_spmf(args.input)
    else:
        raise ValueError("Unsupported input format")
    st = compute_input_stats(records, filename=args.input)

    lines = []
    lines.append(f"input_file: {st.filename}")
    lines.append(f"num_sequences_D: {st.num_sequences}")
    lines.append(f"num_transactions_T: {st.num_transactions}")
    lines.append(f"num_distinct_items_I: {st.num_distinct_items}")
    lines.append("")
    lines.append("transactions_per_sequence:")
    lines.append(f"  min: {st.min_tx_per_seq}")
    lines.append(f"  max: {st.max_tx_per_seq}")
    lines.append(f"  mean: {st.mean_tx_per_seq:.6f}")
    lines.append(f"  std: {st.std_tx_per_seq:.6f}")
    lines.append("")
    lines.append("items_per_transaction:")
    lines.append(f"  min: {st.min_items_per_tx}")
    lines.append(f"  max: {st.max_items_per_tx}")
    lines.append(f"  mean: {st.mean_items_per_tx:.6f}")
    lines.append(f"  std: {st.std_items_per_tx:.6f}")

    text = "\n".join(lines)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)

if __name__ == "__main__":
    main()
