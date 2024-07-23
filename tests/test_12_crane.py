from src.core import OverHeadCrane,JobShop

def test_move():
    OverHeadCrane.MAX_STEPS=30
    agv=OverHeadCrane(1,3,'H1')
    agv.move(4,1,6)
    assert agv.pos[1]==2 and agv.pos[11]==6
    assert agv._last_time==13
    agv.move(15,6,3)
    assert agv.pos[19]==4 and agv.pos[22]==3
    assert agv._last_time==22
    #agv.debug()
def test_hit():
    OverHeadCrane.MAX_STEPS=30
    #assert 2==OverHeadCrane.SAFE_DISTANCE

    c1=OverHeadCrane(1,3,'H1')
    c2=OverHeadCrane(2,6,'H2')
    js=JobShop([c1,c2])
    c1.move(5,3,5)
    assert False==js.is_safe(10)

    
