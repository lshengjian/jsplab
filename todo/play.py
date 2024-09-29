from src.core import Hoist

def test_move():
    agv=Hoist(0,[1,9],'H1',64)
    dt1,dt2=agv.pickup_dropdown(3,9,5)
    print(agv.last_time,dt1,dt2)
    assert agv.last_time==17 and dt1==5 and  dt2==17-5
    #agv.debug()
    assert agv.history[6]==3 and agv.history[7]==3 and agv.history[8]==3 
    dt1,dt2=agv.pickup_dropdown(9,5,0)
    print(agv.last_time,dt1,dt2)
    assert agv.last_time==27 and dt1==0 and  dt2==27-17
    agv.debug()
test_move()