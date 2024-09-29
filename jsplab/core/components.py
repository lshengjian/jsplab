from dataclasses import dataclass as component
from typing import List
from collections import namedtuple,defaultdict

#OpTime = namedtuple("OpTime", "machine_id duration")
class Trajectory:
    def __init__(self):
        self.history=[]
        
class Task:
    def __init__(self,offsets=[],op_time=10):
        self.op_machine_offsets=offsets
        self.op_time:float=op_time
        self.selected_machine_id:int=-1



@component
class TimeStat:
    total_free: float = 0.0
    total_working: float = 0.0




@component
class Machine:
    id:int=0
    init_offset:float=0.0
    offset:float=0.0 
    is_free: bool = True

@component
class Moveable:
    min_offset:float=0 
    max_offset:float=0
    speed:float=1.0

@component
class CanUpDown:
    down_time:float=3.0
    up_time:float=3.0

'''
调度指令
'''
@component
class MoveTarget:
    to_offset:float=0


@component
class Pickup:
    pass
@component
class Dropdown:
    pass

@component
class Job:
    index:int=0
    code:str='A'
    steps:int=3
    step_index=0


