
from dataclasses import dataclass
from typing import List
from copy import deepcopy
@dataclass
class Task:
    op_slot:int=-1
    min_time:int=0
    max_time:int=0
    next_slots:List[int]=None
    op_time:float=-1

    def __str__(self) -> str:
        return f"T{self.cur_op_slot} {self.min_time}->{self.max_time}"

class Job:
    def __init__(self,pcode='A',index=0,tasks:List[Task]=None):
        self.product_code=pcode
        self.job_index:int=index
        self.tasks:List[Task]=deepcopy(tasks)
        self.cur_task_index=0
        
    def select_next_task_slot(self,slot:int):
        assert slot in self.next_slots
        if self.cur_task_index<len(self.tasks)-1:
            self.cur_task_index+=1
        self.cur_task.op_slot=slot


    @property
    def cur_task(self):
        return None if len(self.tasks)<1 else self.tasks[self.cur_task_index]