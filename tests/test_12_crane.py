from src.core import OverHeadCrane,JobShop

def test_move():
    agv=OverHeadCrane(1,3,'H1',30)
    agv.move(1,6,4,2)
    agv.debug()
    assert agv.pos[1]==2 
    assert agv.last_time==15
    agv.move(6,3,15,2)
    agv.debug()
    # assert agv.last_time==18
    # assert agv.pos[16]==3 and agv.pos[17]==3  and agv.pos[18]==3
