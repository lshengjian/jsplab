from jsplab.conf.shop import get_offset,get_operates,get_opkey_dict,get_tanks

import time
def test_read_tanks():
    data=get_operates()
    opkeys=get_opkey_dict(data)
    data=get_tanks('demo1',opkeys)
    assert 4==len(data)
    cfg=data[1]
    assert cfg.op_key==201
def test_read_operates():
    data=get_operates()
    assert 8==len(data)
    cfg=data[101]
    assert 101==cfg.key
    assert '上料'==cfg.name
    assert (50,50,50)==cfg.color
def test_defaut():
    x1=get_offset(1)
    x2=get_offset(2)
    assert x1==1.0 and x2==2.0

def test_read_time():
    start_time = time.perf_counter()
    x1=get_offset(1,'demo1')
    end_time=time.perf_counter()
    dt1=end_time-start_time
    start_time = time.perf_counter()
    x2=get_offset(1,'demo1')
    end_time=time.perf_counter()
    dt2=end_time-start_time
    assert x1==x2 and dt1>dt2*1000

def test_read_diff_shops():
    start_time = time.perf_counter()
    x1=get_offset(1,'demo1')
    end_time=time.perf_counter()
    dt1=end_time-start_time
    x2=get_offset(1,'demo2')
    assert x1==5.0 and x2==3.0