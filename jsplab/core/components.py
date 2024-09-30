from dataclasses import dataclass as component
from typing import List
from collections import namedtuple,defaultdict

#OpTime = namedtuple("OpTime", "machine_id duration")
@component
class Machine:
    id:int=0
    init_offset:float=0.0
    offset:float=0.0
    name:str=''
    #is_free: bool = True
@component
class Locked:  # 如果被已经被计划了，则添加该选项
    machie_entity:int=0

@component
class StartBuff:  # only  TAG
    pass

@component
class EndBuff: # only  TAG
    pass
@component
class OpTank: # only  TAG
    pass
@component
class Hoist:
    down_time:float=3.0
    up_time:float=3.0
    offset_y:int=0

@component
class Moveable:
    min_offset:float=0 
    max_offset:float=0
    speed:float=1.0

class Trajectory:
    def __init__(self):
        self.history=[]
        
    def __str__(self) -> str:
        return f"Trajectory:{self.history}"
# @component
# class Operate:
#     offset: int


@component
class WithTask:
    duration:int=0
    min_time:int=0
    max_time:int=0
    product_code:str='A'
    job_index:int=0
    step_index:int=0

    timer:int=0 
    next_op_name:str=''    

@component
class NeedOut:
    pass

           
# class Task:
#     def __init__(self,offsets=[],op_time=10):
#         self.op_machine_offsets=offsets
#         self.op_time:float=op_time
#         self.selected_machine_ent:int=-1
#         self.timer:int=0

#     def __str__(self) -> str:
#         return f"Task: {self.timer:.0f}/{self.op_time}|{self.op_machine_offsets}"

@component
class TimeStat:
    total_free: float = 0.0
    total_working: float = 0.0










'''
调度指令
'''
@component
class MoveTarget:
    to_offset:float=0
    tank_ent:int=-1


@component
class Pickup:
    timer:float=0
@component
class Dropdown:
    timer:float=0

# @component
# class Job:
#     index:int=0
#     code:str='A'
#     num_tasks:int=3
#     cur_task_index_in_job=0


