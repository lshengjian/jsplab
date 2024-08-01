# from src.core.advanced.machine import Machine,Tank,OverHeadCrane,MachineType
# import numpy as np


# def test_machine():
#     ma=Machine()
#     ma._add_op(0,2)
#     assert ma.last_time==2
#     ma._add_op(8,2)
#     assert ma.last_time==10
#     ma._add_op(2,3)
#     assert ma.last_time==10
#     assert 0.7==(ma.utilization_rate(10))  # (2+2+3)/10
#     assert 'M1[0|70%]: 0->2| 2->5| 8->10|'==str(ma)

# def test_machine2():
#     ma=Machine()
#     ma._add_op(0,2,0,0)
#     ma._add_op(8,2,1,0)
#     ma._add_op(2,3,2,0)
#     assert 'M1[0|70%]:1-1 0->2|3-1 2->5|2-1 8->10|'==str(ma)

# def test_tank_and_crane():
#     Machine.clear()
#     t1=Tank(0,1,'除油1')
#     t2=Tank(1,2,'除油1')
#     h1=OverHeadCrane(2,4,'H1')
#     assert Machine.get_from_cache(0)==t1
#     assert Machine.get_from_cache(1)==t2
#     assert Machine.get_from_cache(2)==h1
#     assert t1.get_machine_type()==MachineType.Tank

#     assert h1.get_machine_type()==MachineType.OverHeadCrane

#     assert '除油1[1|0%]:'==str(t1)

