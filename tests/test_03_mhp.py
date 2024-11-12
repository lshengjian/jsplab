from jsplab.conf.mhp import ConfigMHP

# import time
# start_time = time.perf_counter()
def test_read_data():
    cfg=ConfigMHP('mhp/t4j2.csv')
    assert [0,2,3,6]==cfg.tank_offsets
    assert 4==len(cfg.tank_offsets)
    assert 0==cfg.tank_offsets[0] and 6==cfg.tank_offsets[-1]
    assert 2==cfg.procs[0][1].offset and 3==cfg.procs[1][1].offset

def test_safe():
    hs1=ConfigMHP.get_left_hoists(0,1,3,2)
    assert hs1=={0}
    hs2=ConfigMHP.get_right_hoists(9,8,3,2)
    assert hs2=={2}
    hs1=ConfigMHP.get_left_hoists(0,4,3,2)
    assert hs1=={0,1,2}
    hs2=ConfigMHP.get_right_hoists(9,4,3,2)
    assert hs2=={2,1,0}
    hs1=ConfigMHP.get_left_hoists(0,6.36,3,2)
    assert hs1=={0,1,2}
    hs2=ConfigMHP.get_right_hoists(9,6.36,3,2)
    assert hs2=={2,1}

#   0   1   2   3   4   5   6   7   8   9
#   S|E             X   X           Y   Y
#   |<----------T0----->|
#                   |<------T1--------->|
#   pos(T1)>=pos(T0)+2
