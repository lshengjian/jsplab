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
        self._observers = []
        self._offset=offset
        #self.offset=offset
        self.index=index
        self.name=name if len(name)>0 else f'M{index+1}'
        self.tasks:SortedDict[int,Task]=SortedDict()
        self.last_time=0

    @property
    def offset(self):
        return self._offset
     
    def __str__(self):
        return f'{self.name}[{self.offset}|{self.utilization_rate()*100:.0f}%]'

    def add_subscriber(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_subscriber(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self,event:Event):
        event.sender=self
        event.time_step=self.last_time
        for observer in self._observers:
            #logger.debug(event)
            observer.update(event)

    def update(self,event:Event):
        pass
        #print(f'{event}')

    def get_machine_type(self)->MachineType:
        mts=MachineType.__members__
        cls_name=self.__class__.__name__
        return mts[cls_name]
    


    def utilization_rate(self,cur_time:int=0): 
        total=0
        for task in self.tasks.values():
            if not task.done:
                break
            if cur_time<task.time_finished:
                cur_time=task.time_finished
            total+=task.time_finished-task.time_started
        return total/cur_time if cur_time>0 else 0  
    
    # def get_runtime(self,task:Task,pre:Task=None,next:Task=None,next_machine_index:int=None):
    #     assert self.index in task.eligible_machines
    #     return task._runtimes[self.index]
        
    def assign(self,task:Task)->int: 
        finish_time=self._add_task(task)
        task.time_finished=finish_time
        task.time_started=finish_time-task.runtime
        task.selected_machine=self.index
        task.done=True
        return finish_time
  
    def clean_task(self,task:Task):
        if self.last_time==task.time_finished:
            self.last_time==task.time_started
        self.tasks.pop(task.time_started)


    def _add_task(self,task:Task)->int:
        start=task.time_started
        end=start+task.runtime
        last=0
        found=False
        
        for t,task in self.tasks.items():
            if task.time_started-last>=task.runtime and last<start: #能插进空隙中去
                #self.tasks[start]=task
                found=True
                break
            last=task.time_finished
        if not found:
            if self.last_time>start:
                start=self.last_time
                end=start+task.runtime
            self.last_time=end
        self.tasks[start]=task
        return end

class Comm(Machine):
    pass

class Buff(Machine):
    pass
class Tank(Machine):
    pass

class Transfer(Machine):
    pass
