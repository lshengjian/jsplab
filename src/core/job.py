from __future__ import annotations
from typing import List,Dict
from .task import Task
from .machine import Machine
from .crane import OverHeadCrane
import logging

logger = logging.getLogger(__name__.split('.')[-1])
class Job:

    def __init__(self,index=0,proc_index=0):
        self.index:int=index
        self.proc_index=proc_index
        self.tasks:List[Task]=[]
        self.last_time=0
        self.selected_machine:Machine=None
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
        logger.debug(f'pre:{pre},agv:{crane},next:{next}')
        assert task_index<len(self.tasks) and task_index%2==0
        if self.selected_machine!=None:
            pre=self.selected_machine
        self.selected_machine=next 
        
        op_task=self.cur_task
        op_task.time_started=self.last_time
        if not op_task.is_last and crane!=None:
            agv_task=self.tasks[task_index+1]
            x1=pre.offset
            x2=next.offset
            
            start=pre.assign(op_task,is_mock=True)-op_task.runtime #估计分配
            start=max(start,self.last_time)
            t0=crane.last_time
            dt1,dt2=crane.move(x1,x2,start,op_task.runtime)#这里会修改last_time
            t1=crane.last_time-dt2
            crane.last_time=t0
            op_task.time_finished=t1
            op_task.time_started=t1-op_task.runtime
            pre.assign(op_task) #以天车为准再分配
            logger.debug(f'assign {op_task} to {pre}')

            agv_task.runtime=dt2 #todo 天车提前移动时间小于加工时间，则并行不计
            agv_task.time_started=op_task.time_finished
            self.last_time=crane.assign(agv_task)
            logger.debug(f'assign {agv_task} to {crane}')
            self._cur_task_index+=2
        elif task_index>1:
            agv_task=self.tasks[task_index-1]
            op_task.time_started=agv_task.time_finished
            self.last_time=pre.assign(op_task)
            #self._cur_task_index+=1
            logger.debug(f'assign last {op_task} to {pre}')
        # else:
        #     self.last_time=pre.assign(op_task)
        #     logger.debug(f'assign last {op_task} to {pre}')


    @property 
    def done(self)->int:  
        ds=list(filter(lambda t:t.done,self.tasks))
        return len(ds)==len(self.tasks)

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
          