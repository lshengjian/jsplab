from jsplab.conf.mhp import MultiHoistProblem
from jsplab.core.jobshop import JobShop



def test_make_jobs():
    cfg=MultiHoistProblem('mhp/t4j2.csv')
    shop=JobShop(cfg)
    jobs=shop.make_jobs()
    assert str(jobs[0])=='Job1|CurTask:1\n0 0->999\n2 27->33\n6 0->0\n'


