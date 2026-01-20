from spade.io import read_csv
from spade.vertical import build_vertical_db
from spade.f1 import frequent_items
from spade.node import Node
from spade.dspade import dspade
from spade.bspade import bspade
from spade.maxelts_dspade import maxelts_dspade
from spade.maxelts_bspade import maxelts_bspade

def to_set(nodes):
    return {n.pattern for n in nodes}

def prepare():
    records = read_csv("data/toy_spade.csv")
    vdb = build_vertical_db(records)
    f1 = frequent_items(vdb, minsup=2)
    item_tidlists = {it: tl for (it, tl, _) in f1}
    f1_nodes = [Node(pattern=((it,),), tidlist=tl) for (it, tl, _) in f1]
    return f1_nodes, item_tidlists

def test_maxelts_equals_unlimited_when_large():
    f1_nodes, item_tidlists = prepare()

    dfs = dspade(f1_nodes, item_tidlists, minsup=2)
    bfs = bspade(f1_nodes, item_tidlists, minsup=2)

    # "large" maxElts: in the toy data, the maximum number of elements is 4
    md = maxelts_dspade(f1_nodes, item_tidlists, minsup=2, max_elts=999)
    mb = maxelts_bspade(f1_nodes, item_tidlists, minsup=2, max_elts=999)

    assert to_set(dfs) == to_set(md)
    assert to_set(bfs) == to_set(mb)

def test_maxelts_cuts_long_patterns():
    f1_nodes, item_tidlists = prepare()

    md2 = maxelts_dspade(f1_nodes, item_tidlists, minsup=2, max_elts=2)
    assert all(sum(len(ev) for ev in n.pattern) <= 2 for n in md2)

    mb2 = maxelts_bspade(f1_nodes, item_tidlists, minsup=2, max_elts=2)
    assert all(sum(len(ev) for ev in n.pattern) <= 2 for n in mb2)
