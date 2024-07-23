from __future__ import annotations
from typing import List,Dict
from ..task import Task
from .machine import Machine

class Job:
    cache:Dict[int,Job]={}

    def __init__(self,index=0):
        if Job.cache.get(index,None) is  None:
            self.index:int=index
            self._tasks:List[Task]=[]
            self._last_time=0
            self._last_machine:Machine=None
            self._cur_task_index=0
            Job.cache[index]=self
        else:
            raise ValueError(f"already have a job with id={index}")
         
    @classmethod
    def clean(cls):
        cls.cache.clear()
    def __str__(self):
        rt = f'J{self.index+1}[{self.progress:.2f}] '
        for t in self._tasks:
            rt += f'{t.index+1}:{t.runtime} '
        return rt

    def add_task(self,task:Task):
        if len(self._tasks)>0:
            assert self._tasks[0].job_index==task.job_index
        self._tasks.append(task)


    def assign(self,machine:Machine,next_machine:Machine=None):
        task_index=self._cur_task_index
        assert task_index<self.num_tasks
        task=self._tasks[task_index]
        
        pre=None if task_index==0 else self._tasks[task_index-1]
        next=None if task_index==len(self._tasks)-1 else self._tasks[task_index+1]
        next_mid=None if next_machine is None else next_machine.index
        finish_time=machine.assign(self._last_time,self.index,task,pre,next,next_mid)
        self._last_time=finish_time
        self._last_machine=machine
        if next != None:
            self._cur_task_index+=1
    @property 
    def cur_task_index(self)->int:  
        return self._cur_task_index
            
    @property 
    def cur_task(self)->Task:  
        return self._tasks[self._cur_task_index]
        
    @property 
    def num_tasks(self)->int:  
        return len(self._tasks)

    @property 
    def last_time(self)->int:  
        return self._last_time
    @property 
    def last_machine(self)->Machine:  
        return self._last_machine
    @property 
    def progress(self):  
        total=0
        done=0
        for task in   self._tasks:
            if task.time_finished>0:
                done+=task.runtime
            total+=task.runtime
        rt=0 if total==0 else done/total
        return rt
          