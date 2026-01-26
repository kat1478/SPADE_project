from spade.io import read_csv
from spade.vertical import build_vertical_db
from spade.f1 import frequent_items
from spade.node import Node
from spade.dspade import dspade
from spade.bspade import bspade

def to_set(nodes):
    return {n.pattern for n in nodes}

def test_dspade_bspade_same_patterns():
    records = read_csv("data/wyklad.csv")
    vdb = build_vertical_db(records)
    f1 = frequent_items(vdb, minsup=2)
    item_tidlists = {it: tl for (it, tl, _) in f1}
    f1_nodes = [Node(pattern=((it,),), tidlist=tl) for (it, tl, _) in f1]

    dfs_nodes = dspade(f1_nodes, item_tidlists, minsup=2)
    bfs_nodes = bspade(f1_nodes, item_tidlists, minsup=2)

    assert to_set(dfs_nodes) == to_set(bfs_nodes)

