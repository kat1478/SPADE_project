from __future__ import annotations
import argparse
import subprocess

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--resultsDir", required=True)
    ap.add_argument("--sups", required=True, help="Comma-separated, e.g. 200,300,400")
    ap.add_argument("--maxElts", required=True, help="Comma-separated, e.g. 2,3")
    args = ap.parse_args()

    sups = [int(x.strip()) for x in args.sups.split(",") if x.strip()]
    max_elts_list = [int(x.strip()) for x in args.maxElts.split(",") if x.strip()]

    for sup in sups:
        for e in max_elts_list:
            for alg in ["maxelts-dspade", "maxelts-bspade"]:
                subprocess.check_call([
                    "python", "-m", "scripts.run_and_stat",
                    "--input", args.input,
                    "--alg", alg,
                    "--sup", str(sup),
                    "--maxElts", str(e),
                    "--resultsDir", args.resultsDir,
                ])

if __name__ == "__main__":
    main()
