# SPADE-like Sequential Pattern Mining

A Python implementation of frequent sequential pattern mining algorithms based on the SPADE framework.

## What's included

This repository contains four mining algorithms:

- **dSPADE** — depth-first search variant
- **bSPADE** — breadth-first search variant
- **maxElts-dSPADE** — DFS with a configurable limit on event size
- **maxElts-bSPADE** — BFS with a configurable limit on event size

For each experiment, the implementation produces two output files:

- `OUT_*.txt` — discovered patterns in order of discovery
- `STAT_*.txt` — dataset statistics, runtime metrics, and counters

The algorithms follow the core ideas from:

> Zaki, M. J. (2001). "SPADE: An Efficient Algorithm for Mining Frequent Sequences." _Machine Learning_, 42(1), 31–60.

---

## Getting started

### Requirements

- **Python 3.10** or later (tested with 3.10)
- Linux, macOS, WSL, or Windows

Check your Python version:

```bash
python --version
```

### Installation

Set up a Python virtual environment from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS / WSL
# .venv\Scripts\activate         # Windows (PowerShell)

python -m pip install -U pip
python -m pip install -r requirements.txt
```

If `requirements.txt` is not available, install the minimum dependencies manually:

```bash
python -m pip install pytest matplotlib
```

**Note:** Always activate your virtual environment before running scripts or tests. On systems with mixed `~/.local` and virtual environment packages, this becomes crucial.

---

## Project layout

```
spade/              Core library — I/O, tidlists, joins, pattern representation, algorithms
scripts/            Runnable utilities for experiments, statistics, and plotting
tests/              Unit tests for validation
data/               Input datasets in SPMF format
plots/              Generated charts (PNG)
results*/           Experimental results (OUT and STAT files)
```

---

## Input formats

### SPMF format (.spmf, .spm)

The standard sequential pattern mining format:

- Items are space-separated
- `-1` marks the end of an event (transaction)
- `-2` marks the end of a sequence

Example:

```
1 2 -1 3 -1 -2
1 -1 2 3 -1 -2
```

### CSV format (toy dataset)

For smaller datasets, CSV input is supported. The file should include columns like `sid` (sequence ID), `eid` (event ID), and item columns. See `data/wyklad.csv` and `spade/io.py` for details.

---

## Output files

### OUT\_\*.txt — Discovered patterns

Each line represents one frequent pattern, in discovery order:

```
<pattern_length> <element_count> <tidlist_length> <support> <human_readable_pattern>
```

The header is:
**pattern_len,num_elts,tidlist_len,sup,pattern**
Optionally, the file may start with comment metadata lines beginning with # (algorithm, input, minsup, dataset sizes). These lines can be ignored when parsing.

Example:

```
2 2 3 2 <{B}->{A}>
```

### STAT\_\*.txt — Statistics and timing

Contains comprehensive experiment metadata:

- Dataset statistics: number of sequences (D), transactions (T), items (I), and distribution metrics
- Algorithm parameters: minimum support, optional maxElts limit, algorithm name
- Execution times: reading, mining, writing, and total times
- Performance counters include:
  - `total_discovered` — frequent patterns written to OUT
  - `total_attempted_candidates` — join trials before minsup filtering
  - `total_attempted_sum_tidlist_len` — proxy cost of joins (sum of tidlist lengths during attempted joins)
  - `attempted_len_k` — per-length breakdown of attempted candidates
  - max pattern length

---

## Running experiments

### Compute dataset statistics only

```bash
python -m scripts.compute_stat --input data/msnbc.spmf --out STAT_IO_msnbc.txt
python -m scripts.compute_stat --input data/bike.spmf  --out STAT_IO_bike.txt
python -m scripts.compute_stat --input data/covid.spmf --out STAT_IO_covid.txt
```

### Run a single mining task

Use the main entry point `scripts.run_and_stat`:

**Base algorithms:**

```bash
python -m scripts.run_and_stat --input data/msnbc.spmf --alg dspade --sup 200000 --resultsDir results_final
python -m scripts.run_and_stat --input data/msnbc.spmf --alg bspade --sup 200000 --resultsDir results_final
```

**With maxElts constraint:**

```bash
python -m scripts.run_and_stat --input data/msnbc.spmf --alg maxelts-dspade --sup 200000 --maxElts 2 --resultsDir results_final
python -m scripts.run_and_stat --input data/msnbc.spmf --alg maxelts-bspade --sup 200000 --maxElts 2 --resultsDir results_final
```

**With garbage collection (useful for very large datasets / limited RAM):**

```bash
python -m scripts.run_and_stat --input data/msnbc.spmf --alg bspade --sup 200000 --resultsDir results_final --gc
```

The script prints the paths to generated files:

```
OUT_maxelts-dspade_msnbc_d..._s200000_e2.txt
STAT_maxelts-dspade_msnbc_d..._s200000_e2.txt
```

### Run a parameter sweep

**Grid search — all algorithms:**

```bash
python -m scripts.run_grid \
  --input data/msnbc.spmf \
  --resultsDir results_msnbc \
  --sups 160000,200000,320000 \
  --maxElts 2,3
```

**Grid search — all algorithms with garbage collection:**

```bash
python -m scripts.run_grid \
  --input data/msnbc.spmf \
  --resultsDir results_msnbc \
  --sups 160000,200000,320000 \
  --maxElts 2,3 \
  --gc
```

**Grid search — maxElts variants only:**

```bash
python -m scripts.run_grid_maxelts \
  --input data/covid.spmf \
  --resultsDir results_covid \
  --sups 420,450,480,495 \
  --maxElts 2,3
```

**Grid search — maxElts variants with garbage collection:**

```bash
python -m scripts.run_grid_maxelts \
  --input data/covid.spmf \
  --resultsDir results_covid \
  --sups 420,450,480,495 \
  --maxElts 2,3 \
  --gc
```

---

## Validation

### Run the test suite

```bash
pytest -q
```

All tests should pass. The test suite uses a small toy dataset to validate correctness.

### Consistency checks

For reproducibility, verify that:

- **dSPADE and bSPADE** discover the same set of patterns (though order may differ) for a fixed support threshold.
- **maxElts variants** produce results consistent with the base algorithm when the element limit is not restrictive.

A practical approach is to extract and compare pattern strings from output files as sets.

---

## Generating plots

If matplotlib is installed:

```bash
python -m scripts.make_plots
```

Charts are saved to the `plots/` directory as PNG files.

---

## Troubleshooting

**"No module named 'matplotlib'"**

Install matplotlib into your active environment:

```bash
python -m pip install matplotlib
```

**"No module named 'six'" or other missing packages**

Install missing dependencies:

```bash
python -m pip install six pyparsing python-dateutil
```

**"KeyError: 'sid'" when running compute_stat**

This occurs when the CSV reader is applied to a non-CSV file. Make sure to:

- Use `.csv` input for the CSV reader
- Use `.spmf` input for SPMF datasets
- Verify the CSV file has the expected header columns

---

## Best practices

- **Keep experiment records:** Save the `STAT_*.txt` and `OUT_*.txt` files for each run. Filenames encode the dataset, parameters, and statistics, making results traceable and reproducible.
- **Activate your environment:** Always ensure `.venv` is active before running scripts.
- **Test locally first:** Use the toy dataset (small and fast) to validate your setup before running on larger datasets.

---

## Citation

If you use this implementation in research, please cite:

Zaki, M. J. (2001). SPADE: An Efficient Algorithm for Mining Frequent Sequences. _Machine Learning_, 42(1), 31–60.
