from __future__ import annotations
import argparse
import subprocess

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--resultsDir", required=True)
    ap.add_argument("--sups", required=True, help="Comma-separated, e.g. 2,3,4")
    ap.add_argument("--maxElts", required=False, help="Comma-separated, e.g. 2,3,4 (only for maxelts algs)")
    ap.add_argument("--gc", action="store_true", help="Enable GC checkpoints in run_and_stat")
    args = ap.parse_args()

    sups = [int(x.strip()) for x in args.sups.split(",") if x.strip()]
    max_elts_list = [int(x.strip()) for x in args.maxElts.split(",") if x.strip()] if args.maxElts else []

    for sup in sups:
        # dspade, bspade
        for alg in ["dspade", "bspade"]:
            cmd = [
                "python", "-m", "scripts.run_and_stat",
                "--input", args.input,
                "--alg", alg,
                "--sup", str(sup),
                "--resultsDir", args.resultsDir,
            ]
            if args.gc:
                cmd.append("--gc")
            subprocess.check_call(cmd)

        # maxelts variants
        if max_elts_list:
            for alg in ["maxelts-dspade", "maxelts-bspade"]:
                for e in max_elts_list:
                    cmd = [
                        "python", "-m", "scripts.run_and_stat",
                        "--input", args.input,
                        "--alg", alg,
                        "--sup", str(sup),
                        "--maxElts", str(e),
                        "--resultsDir", args.resultsDir,
                    ]
                    if args.gc:
                        cmd.append("--gc")
                    subprocess.check_call(cmd)

if __name__ == "__main__":
    main()
