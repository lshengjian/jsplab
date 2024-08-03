
from __future__ import annotations
from typing import  List,Dict
from .machine import Machine,Tank,Transfer
from .crane import OverHeadCrane
from .instance import Instance
from .task import Task,extend_tasks
from ..datadef import G
from .job import Job
import numpy as np
import logging
logger = logging.getLogger(__name__.split('.')[-1])

    
class JobShop:
    def __init__(self,ins:Instance):
        self.instance:Instance =ins  

        self.machines:Dict[int,Machine]={}
        self.machine_indexs_locked=set()

        self.cranes:List[OverHeadCrane]=[]
        self.jobs:Dict[int,Job]={}
        
    @property
    def num_jobs(self):
        return len(self.jobs)
    @property
    def num_machines(self):
        return len(self.machines)
    @property
    def num_cranes(self):
        return len(self.cranes)
    @property
    def ends_of_machine_occupancies(self):
        num_machines=self.instance.num_machines
        rt=[0]*num_machines
        for i,m in self.machines.items():
            rt[i]=m.last_time
        return np.array(rt,dtype=float)
    @property
    def last_time(self):
        return round(np.max(self.ends_of_machine_occupancies))   
    def can_select(self,job:Job):
        if job.cur_task.is_last:
            return True
        next_op_task=job.tasks[job.cur_task_index+2]
        ms=list(next_op_task.eligible_machines)
        for m_id in next_op_task.eligible_machines:
            if m_id in self.machine_indexs_locked:
                ms.remove(m_id)
        return len(ms)>0
    def get_next_tasks(self):
        rt=[]
        for job in self.jobs.values():
            rt.append(job.cur_task if not job.cur_task.is_last else None)
        return rt
    def debug(self):
        for task in self.tasks:
            print(task.info)
    def debug_cranes(self):
        for agv in self.cranes:
            agv.debug(self.last_time)
    def reset(self,job_nums_dict={}):
        self.machine_indexs_locked.clear()
        self.jobs.clear()
        tasks=extend_tasks(self.instance.tasks,job_nums_dict)
        #print(len(tasks))
        self.instance.setup(tasks)
        self.machines.clear()
        self.cranes.clear()
        ins=self.instance
        for i in range(ins.num_machines):
            if i<ins.first_crane_index:
                self.machines[i]=Tank(i,ins.machine_offsets[i],ins.machine_names[i])
            else:
                if  isinstance(ins.machine_offsets[i],list):
                    self.machines[i]=Transfer(i,ins.machine_offsets[i],ins.machine_names[i])
                else:
                    self.machines[i]=OverHeadCrane(i,ins.machine_offsets[i],ins.machine_names[i],ins.max_steps,ins.min_offset,ins.max_offset)
                    #todo left canot go to max_offset
                    self.cranes.append(self.machines[i])


        
        for task in tasks:
            if task.job_index not in self.jobs:
                self.jobs[task.job_index]=Job(task.job_index,task.product_index)
            job=self.jobs[task.job_index]
            job.add_task(task)
        self.tasks=tasks
        for agv in self.cranes:
            for c in self.cranes:
                if agv!=c:
                    agv.add_subscriber(c)

    def lock(self,tank:Machine):
        self.machine_indexs_locked.add(tank.index)
    def unlock(self,tank:Machine):
        self.machine_indexs_locked.remove(tank.index)
    def is_lock(self,tank_idx:int):
        return tank_idx in self.machine_indexs_locked
    
    def get_job_pos(self,step:int,job:Job)->int:
        data=sorted(job.tasks,key=lambda t:t.time_started)
        for task in data:
            if step<task.time_started and task.index==0:
                return -1
            if step<=task.time_finished:
                break
        if task.index%2==0 and not task.is_last:
            x= self.instance.machine_offsets[task.selected_machine]
            if isinstance(x,list):
                x=x[1] if task.done else x[0]
            return x
        for agv in self.cranes:
            if agv.index==task.selected_machine and not task.is_last:
                return agv.pos[step]
        return -1

    def is_safe(self,max_time:int)->bool:
        
        cranes=self.cranes
        num_agvs=len(cranes)
        for t in range(max_time):
            for i in range(num_agvs-1):
                j=i+1
                dis=G.CRANE_SAFE_DISTANCE
                x1=cranes[i].pos[t]
                x2=cranes[j].pos[t]
                if abs(x1-x2) < dis or x1+2>x2:
                    logger.debug(f'time:{t} {cranes[i]} pos:{x1} hit {cranes[j]} pos:{x2}')
                    cranes[i].debug(max_time)
                    cranes[j].debug(max_time)
                    return False
                    #raise ValueError(f'{cache[i]} hit {cache[j]}')
        return True


            


    def check_done(self) -> bool:
        for job in self.jobs.values():
            if not job.done:
               return False
        return True

    def choose_machine(self, task: Task) -> int:
        """
        This function performs the logic, with which the machine is chosen (in the case of the flexible JSSP)
        Implemented at the moment: Choose the machine out of the set of possible machines with the earliest possible
        start time

        :param task: Task

        :return: Machine on which the task will be scheduled.

        """
        now=self.last_time
        possible_machines = task.machines.copy() #copy
        for i,v in enumerate(possible_machines):
            if v>0 and self.is_lock(i):
                possible_machines[i]=0
        if sum(possible_machines)<1:
            raise ValueError(f'{task} not eligible machines now') #return -1 
        d=np.ones_like(possible_machines)
        for i,m in self.machines.items():
            d[i]=1+m.utilization_rate(now)

            
        machine_times = np.where(possible_machines,
                                 self.ends_of_machine_occupancies*d,
                                 np.full(len(possible_machines), np.inf))
        return int(np.argmin(machine_times)) 







 

 # class NodeType(IntEnum): 
#     Machine = 0 
#     Task = 1 

# '''
# 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0
# ---节点类型
#     -offset
#       -利用率|进度百分比
# '''
# class NodeState:
#     def __init__(self):
#         self.data=np.zeros(100,dtype=float)