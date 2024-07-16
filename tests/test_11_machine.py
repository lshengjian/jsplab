from src.core import Machine
import numpy as np


def test_machine():
    ma=Machine()
    ma.add_op(0,2)
    assert ma.last_time==2
    ma.add_op(8,2)
    assert ma.last_time==10
    ma.add_op(2,3)
    assert ma.last_time==10
    assert 0.7==(ma.utilization_rate(10))  # (2+2+3)/10
    assert 'M1[0.70]: 0->2| 2->5| 8->10|'==str(ma)

def test_machine2():
    ma=Machine()
    ma.add_op(0,2,0,0)
    ma.add_op(8,2,1,0)
    ma.add_op(2,3,2,0)
    assert 'M1[0.70]:1-1 0->2|3-1 2->5|2-1 8->10|'==str(ma)
