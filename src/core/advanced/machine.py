from __future__ import annotations
from collections import namedtuple,defaultdict
from typing import List,Dict
from enum import IntEnum
from ..task import Task
from ..crane_state import make_crane_states
OpInfo = namedtuple("OpInfo", "start end job_idx task_idx")#加工处理数据

class MachineType(IntEnum): 
    Comm = 0 #保留不用
    Buff = 1 #暂存
    Tank = 2 #加工
    OverHeadCrane = 4 #同时具备垂直、横向运动的天车
    Transfer=8 #只能垂直或横向移动的转运小车
 
    
class Machine:
    cache:Dict[int,Machine]={}
    offset_cache:Dict[int,Machine]={}
    def __init__(self,index=0,offset=0,name=''):
        self.index=index
        self.offset=offset
        self.name=name if len(name)>0 else f'M{index+1}'
        
        self.ops:List[OpInfo]=[] 
        self._last_time=0
        
    

    def add2cache(self):
        if Machine.cache.get(self.index,None):
            raise ValueError(f"already have a machine with id={self.index}")
        else:
            Machine.cache[self.index]=self
            mt=self.get_machine_type()
            if mt<=MachineType.Tank:
                Machine.offset_cache[self.offset]=self
            

    @classmethod
    def clear(cls):
        cls.cache.clear()
        Machine.offset_cache.clear()

    def get_machine_type(self)->MachineType:
        mts=MachineType.__members__
        cls_name=self.__class__.__name__
        return mts[cls_name]
    
    @classmethod
    def get_from_cache(cls,index:int):
        return  Machine.cache.get(index,None)
    @classmethod
    def get_from_offset(cls,index:int):
        return  Machine.offset_cache.get(index,None)    
    
    def get_runtime(self,task:Task,pre:Task=None,next:Task=None,next_machine_index:int=None):
        assert self.index in task.eligible_machines
        return task._runtimes[self.index]
        
    def assign(self,last_time:int,job_idx:int,task:Task,pre:Task=None,next:Task=None,next_machine_index:int=None)->int: 
        op_time=self.get_runtime(task,pre,next,next_machine_index)
        finish_time=self._add_op(last_time,op_time,job_idx,task.index)
        task.time_finished=finish_time
        task.time_started=finish_time-op_time
        task.runtime=op_time
        task.selected_machine=self.index
        return  finish_time  
               
    def _add_op(self,start:int,duration:int,job_idx=-1 ,task_idx=-1)->int:
        end=start+duration
        last=0
        found=False
        
        for op in self.ops:
            if op.start-last>=duration and last<=start: #能插进空隙中去
                self.ops.append(OpInfo(start,end,job_idx,task_idx))
                found=True
                break
            last=op.end
        if not found:
            if self._last_time>start:
                end=self._last_time+duration
                self.ops.append(OpInfo(self._last_time,end,job_idx ,task_idx))
                self._last_time+=duration
            else:
                self.ops.append(OpInfo(start,end,job_idx ,task_idx))
                self._last_time=end
        self.ops.sort()
        return end
    
    @property 
    def last_time(self):  
        return self._last_time

    def utilization_rate(self,cur_time:int=0): 
        total=0
        for op in self.ops:
            if cur_time<op.end:
                cur_time=op.end
            total+=op.end-op.start
        return total/cur_time if cur_time>0 else 0
    
    def __str__(self):
        rt = f'{self.name}[{self.offset}|{self.utilization_rate()*100:.0f}%]:'
        for op in self.ops:
            name =''  if op.job_idx<0 and op.task_idx<0 else f'{op.job_idx+1}-{op.task_idx+1}'
            rt += f'{name} {op.start}->{op.end}|'
        return    rt 
class Comm(Machine):
    def __init__(self,index=0,offset=0,name=''):
        super().__init__(index,offset,name)
        self.add2cache()
class Buff(Comm):
    pass
class Tank(Comm):
    pass
class OverHeadCrane(Comm):

    def get_runtime(self,task:Task,pre:Task=None,next:Task=None,next_machine_index:int=None):
        assert self.index in task.eligible_machines
        
        x1=self.offset
        x2=Machine.get_from_cache(pre.selected_machine).offset
        if next_machine_index is None:
            x3=x2
        else:
            x3=Machine.get_from_cache(next_machine_index).offset
        self.offset=x3
        return abs(x3-x2)+2+2


    # def __str__(self):
    #     rt = ''
    #     pos=[]
    #     for op in self.ops:
    #         pass
    #     return    rt 
class Transfer(Comm):
    pass
if __name__ == "__main__":
    ma=Machine()
    #  [0,2]   [8,2]
    ma._add_op(0,2)
    assert ma.last_time==2
    ma._add_op(8,2)
    assert ma.last_time==10
    ma._add_op(2,3)
    #print(ma.ops)
    assert ma.last_time==10
    print(ma.utilization_rate(10))
    print(ma)
