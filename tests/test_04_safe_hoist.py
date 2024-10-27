from jsplab.conf.mhp import MultiHoistProblem

# import time
# start_time = time.perf_counter()
def test_bound():
    p=MultiHoistProblem('mhp/t4j2.csv',2)
    bd=p.get_hoist_bound(0)
    assert (0,4)==bd
    bd=p.get_hoist_bound(1)
    assert (2,6)==bd

def test_validate_hoists():
    p=MultiHoistProblem('mhp/t4j2.csv',2)
    hs=p.select_hoists_by_offset(0)
    assert [0]==hs
    hs=p.select_hoists_by_offset(1)
    assert [0]==hs
    hs=p.select_hoists_by_offset(2)
    assert [0,1]==hs
    hs=p.select_hoists_by_offset(3)
    assert [0,1]==hs
    hs=p.select_hoists_by_offset(4)
    assert [0,1]==hs
    hs=p.select_hoists_by_offset(5)
    assert [1]==hs
    hs=p.select_hoists_by_offset(6)
    assert [1]==hs