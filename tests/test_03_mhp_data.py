from jsplab.conf.mhp import MultiHoistProblem
from jsplab.core.job import Job
# import time
# start_time = time.perf_counter()
def test_read_data():
    cfg=MultiHoistProblem('mhp/h2j2.csv')
    assert [0,2,3,6]==cfg.tank_offsets
    assert 4==len(cfg.tank_offsets)
    assert 0==cfg.tank_offsets[0] and 6==cfg.tank_offsets[-1]
    assert 2==cfg.procs[0][1].offset and 3==cfg.procs[1][1].offset

def test_make_jobs():
    cfg=MultiHoistProblem('mhp/h2j2.csv')
    jobs=Job.make_jobs(cfg,2)
    assert str(jobs[0])=='Job1|CurTask:1\n0 0->999\n2 9->20\n6 0->0\n'

#   0   1   2   3   4   5   6   7   8   9
#   S|E             X   X           Y   Y
#   |<----------T0----->|
#                   |<------T1--------->|
#   pos(T1)>=pos(T0)+2
