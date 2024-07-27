from src.core import OverHeadCrane,JobShop

def test_move():
    agv=OverHeadCrane(1,3,'H1',30,2,2)
    agv.move(1,6,4)
    agv.debug()
    assert agv.pos[1]==2 and agv.pos[11]==6
    assert agv.last_time==13
    agv.move(6,3,15)
    assert agv.pos[19]==4 and agv.pos[22]==3
    assert agv.last_time==22
    agv.debug()
# def test_event():
#     c1=OverHeadCrane(1,3,'H1',30,2,2)
#     c2=OverHeadCrane(2,6,'H2',30,2,2)
#     c1.add_subscriber(c2)
#     c1.move(3,0,5)
#     assert [3,10]==list(c2.avoids.keys())
#     assert -2==c2.avoids[3].offset and -1==c2.avoids[3].dir
#     assert 7==c2.avoids[10].offset and 1==c2.avoids[10].dir
#     # for k,v in c2.avoids.items():
#     #     print(k,v)

    
