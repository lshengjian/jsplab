
from dataclasses import dataclass
from typing import List
from copy import deepcopy
from jsplab.conf.mhp import MultiHoistProblem,ProcStep
class Task:
    def __init__(self,cfg:ProcStep):
        self.cfg:ProcStep=cfg
        self.op_time:float=-1
        self.can_move_hoists:List[int]=[]
        self.select_hoist=None

    def __str__(self) -> str:
        return f"{self.cfg.offset} {self.cfg.min_time}->{self.cfg.max_time}"#{self.op_time}|{self.select_hoist}

class Job:
    def __init__(self,index=0,tasks:List[Task]=None):
        #self.product_code=pcode
        self.job_index:int=index
        self.tasks:List[Task]=tasks   #deepcopy(tasks)
        self.cur_task_index=0
    def __str__(self) -> str:
        msg= f"Job{self.job_index+1}|CurTask:{self.cur_task_index+1}\n"
        for t in self.tasks:
            msg+=str(t)+'\n'
        return msg
    @staticmethod
    def make_jobs(num_hoists=2,fname='mhp/h2j2.csv'):
        cfg=MultiHoistProblem('mhp/h2j2.csv')
        offsets=cfg.tank_offsets
        min_offset,max_offset=min(offsets),max(offsets)
        rt=[]
        for job_index,proc in enumerate(cfg.procs):
            tasks=[]
            for step in proc:
                task=Task(step)
                if step.offset==min_offset:
                    task.can_move_hoists=[0]
                elif step.offset==max_offset:
                    task.can_move_hoists=[num_hoists-1]
                else:
                    task.can_move_hoists=list(range(num_hoists)) #todo fix by safe distance
                tasks.append(task)
            rt.append(Job(job_index,tasks))
        return rt


    # def select_next_task_slot(self,slot:int):
    #     assert slot in self.next_slots
    #     if self.cur_task_index<len(self.tasks)-1:
    #         self.cur_task_index+=1
    #     self.cur_task.op_slot=slot


    @property
    def cur_task(self):
        return None if len(self.tasks)<1 else self.tasks[self.cur_task_index]