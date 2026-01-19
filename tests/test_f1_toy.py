from spade.io import read_csv
from spade.vertical import build_vertical_db, support
from spade.f1 import frequent_items

def test_f1_toy_sup2():
    records = read_csv("data/toy_spade.csv")
    vdb = build_vertical_db(records)

    f1 = frequent_items(vdb, minsup=2)
    got = {it: sup for (it, tidlist, sup) in f1}

    assert got == {"A": 4, "B": 4, "D": 2, "F": 4}

def test_support_counts_unique_sid():
    tidlist = [(1, 10), (1, 20), (2, 15)]
    assert support(tidlist) == 2
