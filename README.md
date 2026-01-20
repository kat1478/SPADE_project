# SPADE-like Sequential Pattern Mining (dSPADE / bSPADE / maxElts-\*)

This repository contains a Python implementation of SPADE-like frequent sequential pattern mining:

- **dSPADE** (depth-first search)
- **bSPADE** (breadth-first search)
- **maxElts-dSPADE** (DFS with a limit on the number of elements in an event)
- **maxElts-bSPADE** (BFS with a limit on the number of elements in an event)

The project produces two output files per experiment:

- **OUT\_\*.txt** (discovered patterns in discovery order)
- **STAT\_\*.txt** (dataset statistics + timing + counters)

Reference:

> Mohammed J. Zaki, "SPADE: An Efficient Algorithm for Mining Frequent Sequences", Machine Learning 42(1), 2001.

---

## 1) Requirements

### Python

- Recommended: **Python 3.10** (tested)
- Works with: Python 3.9+ (should)

Check:

```bash
python --version
```

### OS

Tested on Linux/WSL. Should work on macOS/Windows (with Python 3.10+).

---

## 2) Installation

```bash
python -m pip install pytest
python -m pip install matplotlib
```

---

## 3) Project structure

- `spade/` – core library (I/O, tidlists, joins, pattern representation, mining algorithms)
- `scripts/` – runnable CLI utilities (experiments, statistics, plots)
- `tests/` – unit tests (toy dataset validation)
- `data/` – datasets (toy + real datasets in SPMF format)
- `results*/` – generated results (OUT/STAT)
- `plots/` – generated charts

---

## 4) Input data formats

### 4.1 SPMF format (`.spmf`, `.spm`)

- Items separated by spaces
- `-1` ends an event (transaction)
- `-2` ends a sequence

Example:

```
1 2 -1 3 -1 -2
1 -1 2 3 -1 -2
```

### 4.2 CSV (toy dataset)

A small toy dataset can be provided as CSV. The CSV reader expects a specific header
(e.g., `sid`, etc.). See `spade/io.py` and the toy file in `data/`.

---

## 5) Outputs

### 5.1 OUT file (`OUT_*.txt`)

Each discovered frequent pattern is written in a separate line, in discovery order:

- pattern length (positions)
- number of elements
- tidlist length
- support (`sup`)
- the pattern (human-readable)

Example line:

```
2 2 3 2 <{B}->{A}>
```

### 5.2 STAT file (`STAT_*.txt`)

Contains:

- dataset stats (`D`, `T`, `I`, min/max/mean/std)
- parameters (`sup`, optional `maxElts`, algorithm name)
- partial times: reading, mining, writing
- total times (including and excluding read)
- counters: candidates, discovered patterns, per-length breakdown

---

## 6) User manual (how to run)

### 6.1 Dataset statistics only

```bash
python -m scripts.compute_stat --input data/msnbc.spmf --out STAT_IO_msnbc.txt
python -m scripts.compute_stat --input data/bike.spmf  --out STAT_IO_bike.txt
python -m scripts.compute_stat --input data/covid.spmf --out STAT_IO_covid.txt
```

### 6.2 Run a single experiment (OUT + STAT)

Main entry point:

**Base algorithms**

```bash
python -m scripts.run_and_stat --input data/msnbc.spmf --alg dspade --sup 200000 --resultsDir results_final
python -m scripts.run_and_stat --input data/msnbc.spmf --alg bspade --sup 200000 --resultsDir results_final
```

**maxElts algorithms**

```bash
python -m scripts.run_and_stat --input data/msnbc.spmf --alg maxelts-dspade --sup 200000 --maxElts 2 --resultsDir results_final
python -m scripts.run_and_stat --input data/msnbc.spmf --alg maxelts-bspade --sup 200000 --maxElts 2 --resultsDir results_final
```

The script prints paths to generated files, e.g.:

- `OUT_maxelts-dspade_msnbc_d..._s200000_e2.txt`
- `STAT_maxelts-dspade_msnbc_d..._s200000_e2.txt`

### 6.3 Run a parameter grid (multiple sups / maxElts)

**Full grid (base + maxElts variants)**

```bash
python -m scripts.run_grid \
  --input data/msnbc.spmf \
  --resultsDir results_msnbc \
  --sups 160000,200000,320000 \
  --maxElts 2,3
```

**maxElts-only grid**

```bash
python -m scripts.run_grid_maxelts \
  --input data/covid.spmf \
  --resultsDir results_covid \
  --sups 420,450,480,495 \
  --maxElts 2,3
```

---

## 7) Correctness checks

### 7.1 Unit tests (toy dataset)

```bash
pytest -q
```

Expected: all tests pass.

### 7.2 Consistency checks (recommended)

For a fixed `sup`:

- dSPADE and bSPADE should discover the same set of patterns (order may differ).
- maxElts variants should be consistent with base variants when `maxElts` does not restrict patterns.

---

## 8) Plotting

If `matplotlib` is installed:

```bash
python -m scripts.make_plots
```

Plots are saved under `plots/` (PNG).

---

## 9) Troubleshooting

### 9.1 `ModuleNotFoundError: No module named 'matplotlib'`

Install it into the active environment:

```bash
python -m pip install matplotlib
```

### 9.2 Errors like `No module named 'six'` / `pyparsing`

Install missing dependencies:

```bash
python -m pip install six pyparsing python-dateutil
```

### 9.3 `KeyError: 'sid'` when running `compute_stat`

This usually happens when the CSV reader is used on a non-CSV file.
Make sure you pass a `.csv` file with the expected header, or use `.spmf` input.

---

## 10) Citation

- M. J. Zaki, "SPADE: An Efficient Algorithm for Mining Frequent Sequences", Machine Learning 42(1), 2001.
