from jsplab.core.hoist import Hoist,HoistCfg


def test_ETA():
    cfg=HoistCfg(0,1,1,1,'H1',1,0,10,6,6)
    h=Hoist(cfg)
    assert 'H1|0 D:1.0 V:1 T1:1.0 T2:1.0'==str(h)
    assert 6.0==h.ETA(5) #1+4/1+1
    assert 2.0==h.ETA(1) #1+1
    assert 1.4142135623730951==h.ETA(0.5) #sqrt(0.5)*2
    assert 0.6324555320336759==h.ETA(0.1) 
    assert 0==h.ETA(0)


def test_plan():
    cfg=HoistCfg(0,1,1,1,'H1',1,0,10,6,6)
    h=Hoist(cfg)
    assert 6.0==h.ETA(5) #1+4/1+1
    assert 0==h.plan(5,0)
    assert 0.5==h.plan(5,1)
    assert 1.5==h.plan(5,2)
    assert 2.5==h.plan(5,3)
    assert 3.5==h.plan(5,4)
    assert 4.5==h.plan(5,5)
    assert 5.0==h.plan(5,6)
    assert 5.0==h.plan(5,16)

def test_plan2():
    cfg=HoistCfg(0,2,1,1,'H1',1,0,10,6,6)
    h=Hoist(cfg)
    assert 5.75==h.ETA(5)
    assert 0==h.plan(5,0)
    assert 0.75==h.plan(5,1)
    assert 1.75==h.plan(5,2)
    assert 2.75==h.plan(5,3)
    assert 3.75==h.plan(5,4)
    assert 4.71875==h.plan(5,5)
    assert 5.0==h.plan(5,6)