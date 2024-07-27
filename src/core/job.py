from __future__ import annotations
from typing import List,Dict
from .task import Task
from .machine import Machine
from .crane import OverHeadCrane

class Job:

    def __init__(self,index=0):
        self.index:int=index
        self.tasks:List[Task]=[]
        self.last_time=0
        #self.last_machine:Machine=None
        self._cur_task_index=0
       

    def __str__(self):
        rt = f'J{self.index+1}[{self.progress:.2f}] '
        for t in self.tasks:
            rt += f'{t.index+1}:{t.runtime} '
        return rt

    def add_task(self,task:Task):
        if len(self.tasks)>0:
            self.tasks[-1].is_last=False
            assert self.tasks[0].job_index==task.job_index
        task.done=False
        #task.selected_machine=None
        task.time_finished=0
        task.time_started=0
        self.tasks.append(task)
        task.is_last=True


    def assign(self,crane:OverHeadCrane,pre:Machine,next:Machine=None):
        task_index=self._cur_task_index
        
        assert task_index<len(self.tasks) and task_index%2==0  
        op_task=self.tasks[task_index]
        start=pre.assign(op_task)-op_task.runtime #估计分配
        #op_task.done=False
        pre.clean_task(op_task)
        
        if not op_task.is_last and crane!=None:
            agv_task=self.tasks[task_index+1]
            x1=pre.offset
            x2=next.offset
            dt,t1=crane.move(x1,x2,start)
            op_task.time_finished=t1
            op_task.time_started=t1-op_task.runtime
            pre.assign(op_task) #以天车为准再分配
            agv_task.runtime=dt
            agv_task.time_started=op_task.time_finished
            crane.assign(agv_task)
            self._cur_task_index+=2
        elif op_task.is_last:
            agv_task=self.tasks[task_index-1]
            op_task.time_started=agv_task.time_finished
            pre.assign(op_task)



    @property 
    def cur_task_index(self)->int:  
        return self._cur_task_index
            
    @property 
    def cur_task(self)->Task:  
        return self.tasks[self._cur_task_index]
        
    @property 
    def num_tasks(self)->int:  
        return len(self.tasks)

    @property 
    def progress(self):  
        total=0
        done=0
        for task in   self.tasks:
            if task.time_finished>0:
                done+=task.runtime
            total+=task.runtime
        rt=0 if total==0 else done/total
        return rt
          