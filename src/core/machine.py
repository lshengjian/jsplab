from __future__ import annotations
from collections import namedtuple,defaultdict
from dataclasses import dataclass 
from typing import List,Dict
from enum import IntEnum
from .task import Task
from ..datadef.events import *
from sortedcontainers import SortedDict
import logging

logger = logging.getLogger(__name__.split('.')[-1])


class MachineType(IntEnum): 
    Comm = 0 #保留不用
    Buff = 1 #暂存
    Tank = 2 #加工
    OverHeadCrane = 4 #同时具备垂直、横向运动的天车
    Transfer=8 #只能垂直或横向移动的转运小车
    

class Machine:
    def __init__(self,index=0,offset=0,name=''):
        
        self._offset=offset
        #self.offset=offset
        self.index=index
        self.name=name if len(name)>0 else f'M{index+1}'
        self.sort_tasks:SortedDict[int,Task]=SortedDict()
        self.last_time=0

    def reset(self):
        self.last_time=0
        self.sort_tasks.clear() 

    @property
    def offset(self):
        return self._offset
     
    def __str__(self):
        return f'{self.name}[{self._offset}|{self.utilization_rate()*100:.0f}%]'

    def get_machine_type(self)->MachineType:
        mts=MachineType.__members__
        cls_name=self.__class__.__name__
        return mts[cls_name]
    


    def utilization_rate(self,cur_time:int=0): 
        total=0
        for task in self.sort_tasks.values():
            if not task.done:
                break
            if cur_time<task.time_finished:
                cur_time=task.time_finished
            total+=task.runtime
        return total/cur_time if cur_time>0 else 0  
   

        
    def assign(self,task:Task,is_mock=False)->int: 
        finish_time=self._add_task(task,is_mock)
        if not is_mock:
            task.time_finished=finish_time
            task.time_started=finish_time-task.runtime
            task.selected_machine=self.index
            task.done=True
            if self.last_time<finish_time:
                self.last_time=finish_time
        return finish_time
  


    def _add_task(self,task:Task,is_mock=False)->int:
        start=task.time_started
        end=start+task.runtime
        last=0
        found=False
        
        for _,t in self.sort_tasks.items():
            if t.time_started-last>=task.runtime and last<start: #能插进空隙中去
                #self.tasks[start]=task
                found=True
                break
            last=t.time_finished
        if not found:
            if self.last_time>start:
                start=self.last_time
                end=start+task.runtime

        if not is_mock:
            self.sort_tasks[start]=task
        return end

class Comm(Machine):
    pass

class Buff(Machine):
    pass
class Tank(Machine):
    pass

class Transfer(Machine):
    def __init__(self,index=0,offsets=[],name=''):
        super().__init__(index,offsets,name)
        self.x1=offsets[0]
        self.x2=offsets[1]
        self._offset=offsets[0]
    def reset(self):
        self.last_time=0 
        self._offset=self.x1
        
    def assign(self,task:Task)->int: 
        rt=super().assign(task)
        self.last_time+=task.runtime#go back to begin offset
        return rt