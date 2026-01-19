from spade.join import i_join, s_join

def test_i_join_intersection():
    t1 = [(1,10), (1,20), (2,10)]
    t2 = [(1,20), (2,10), (2,15)]
    assert i_join(t1, t2) == [(1,20), (2,10)]

def test_s_join_strictly_after():
    # t1: occurrences of prefix end event
    t1 = [(1,10), (1,20), (2,5)]
    # t2: occurrences of extension end event
    t2 = [(1,10), (1,15), (1,25), (2,5), (2,6)]
    # valid if exists eid1 < eid2 within same sid:
    # sid=1: for eid2=15 there is 10 < 15; for 25 there is 10/20 < 25
    # sid=2: for eid2=6 there is 5 < 6; eid2=5 is NOT allowed (must be strictly after)
    assert s_join(t1, t2) == [(1,15), (1,25), (2,6)]
