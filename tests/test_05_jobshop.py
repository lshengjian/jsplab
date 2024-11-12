from jsplab.conf.mhp import ConfigMHP
from jsplab.core.mhp import MultiHoistProblem



def test_make_jobs():
    cfg=ConfigMHP('mhp/t4j2.csv')
    shop=MultiHoistProblem(cfg)
    jobs=shop.make_jobs()
    assert str(jobs[0])=='Job1|CurTask:1\n0 0->999\n2 27->33\n6 0->0\n'


