from __future__ import annotations
import argparse
import subprocess

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--resultsDir", required=True)
    ap.add_argument("--sups", required=True, help="Comma-separated, e.g. 2,3,4")
    ap.add_argument("--maxElts", required=False, help="Comma-separated, e.g. 2,3,4 (only for maxelts algs)")
    args = ap.parse_args()

    sups = [int(x.strip()) for x in args.sups.split(",") if x.strip()]
    max_elts_list = [int(x.strip()) for x in args.maxElts.split(",") if x.strip()] if args.maxElts else []

    algs = ["dspade", "bspade", "maxelts-dspade", "maxelts-bspade"]

    for sup in sups:
        # dspade, bspade
        for alg in ["dspade", "bspade"]:
            subprocess.check_call([
                "python", "-m", "scripts.run_and_stat",
                "--input", args.input,
                "--alg", alg,
                "--sup", str(sup),
                "--resultsDir", args.resultsDir,
            ])

        # maxelts variants
        if max_elts_list:
            for alg in ["maxelts-dspade", "maxelts-bspade"]:
                for e in max_elts_list:
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
