from .task import Task
from .machine import Machine
from typing import List
import numpy as np

class Job:
    def __init__(self,index=0):
        self.index:int=index
        self._tasks:List[Task]=[]
        self._last_time=0
        self._last_machine:Machine=None
        self._cur_task_index=0

    def __str__(self):
        rt = f'J{self.index+1}: {self.progress}'
        for t in self._tasks:
            rt += f'{t.task_index+1}:{t.runtime} '
        return rt

    def add_task(self,task:Task):
        if len(self._tasks)>0:
            assert self._tasks[0].job_index==task.job_index
        self._tasks.append(task)


    def assign(self,machine:Machine):
        task_index=self._cur_task_index
        assert task_index<self.num_tasks
        task=self._tasks[task_index]
        m_idx=machine.index
        op_time=task._runtimes[m_idx]
        ft=machine.add_op(self._last_time,op_time,self.index,task_index)
        self._last_time=ft
        self._last_machine=machine
        task.finished=1
        task.started=ft-op_time
        task.runtime=op_time
        self._cur_task_index+=1

    def greedy_select(self,ms:List[Machine])->Machine:
        op_times=np.array(self.cur_task._runtimes)
        op_times[op_times<1]=9999 # todo
        for i,t in enumerate(op_times):
            op_times[i]=t*(1+ms[i].utilization_rate(self._last_time))
        idxs=np.argsort(op_times)
        return ms[idxs[0]]

        
    @property 
    def cur_task(self)->int:  
        return self._tasks[self._cur_task_index]
        
    @property 
    def num_tasks(self)->int:  
        return len(self._tasks)

    @property 
    def last_time(self)->Machine:  
        return self._last_time
    @property 
    def last_machine(self)->Machine:  
        return self._last_machine
    @property 
    def progress(self):  
        total=0
        done=0
        for task in   self._tasks:
            if task.finished>0:
                done+=task.runtime
            total+=task.runtime
        rt=0 if total==0 else done/total
        return rt
          