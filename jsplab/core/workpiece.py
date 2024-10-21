from jsplab.cbd import Component,EventManager
from jsplab.conf import G
from dataclasses import dataclass
from typing import List
@dataclass
class Task:
    cur_op_slot:int=0
    min_time:int=0
    max_time:int=0
    next_slots:List[int]=None

    def __str__(self) -> str:
        return f"T{self.cur_op_slot} {self.min_time}->{self.max_time}"

class Workpiece(Component):
    def __init__(self):
        super().__init__()
        self.product_code='A'
        self.job_index:int=0
        self.tasks:List[Task]=[Task(3,10,20)]
        self.cur_task_index=0
        

    @property
    def cur_task(self):
        return None if len(self.tasks)<1 else self.tasks[self.cur_task_index]