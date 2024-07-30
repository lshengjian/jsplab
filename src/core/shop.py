
from __future__ import annotations
from typing import  List,Dict
from .machine import Machine,Tank,Transfer
from .crane import OverHeadCrane
from .instance import Instance
from .task import Task,extend_tasks
from collections import defaultdict
from .job import Job
import numpy as np
class JobShop:
    def __init__(self,ins:Instance,max_steps=30,safe_distance=2,job_nums_dict={},):
        # config = OmegaConf.load("conf/constant.yaml")
        # self.args:Constant = get_dataclass_by_name('Constant')(**config)
        self.instance:Instance =ins  
          
        self.safe_distance=safe_distance 
        self.machines:Dict[int,Machine]={}
        self.cranes:List[OverHeadCrane]=[]
        self.jobs:Dict[int,Job]={}
        for i in range(ins.num_machines):
            if i<ins.first_crane_index:
                self.machines[i]=Tank(i,ins.machine_offsets[i],ins.machine_names[i])
            else:
                if  isinstance(ins.machine_offsets[i],list):
                    self.machines[i]=Transfer(i,ins.machine_offsets[i],ins.machine_names[i])
                else:
                    self.machines[i]=OverHeadCrane(i,ins.machine_offsets[i],ins.machine_names[i],max_steps)
                    self.cranes.append(self.machines[i])
        tasks=extend_tasks(ins.tasks,job_nums_dict)
        for task in tasks:
            if task.job_index not in self.jobs:
                self.jobs[task.job_index]=Job(task.job_index)
            job=self.jobs[task.job_index]
            job.add_task(task)

 

    # def get_job_pos(self,step:int,job_id:int,tasks:List[Task])->int:
    #     data=filter(lambda t:t.job_index==job_id,tasks)
    #     data=sorted(list(data),key=lambda t:t.time_started)
    #     for i,task in enumerate(data):
    #         if step<task.time_started and task.index==0:
    #             return -1
    #         if step<=task.time_finished:
    #             break
    #     if step>task.time_finished:
    #         return -1
    #     if task.index%2==0:
    #         return self.instance.machine_offsets[task.selected_machine]
    #     for agv in self.machines.values():
    #         if agv.index==task.selected_machine and not task.is_last:
    #             return agv.pos[step]
    #     return -1
    def is_safe(self,max_time:int)->bool:
        
        cranes=list(filter(lambda m:isinstance(m,OverHeadCrane),self.machines.values()))
        num_agvs=len(cranes)
        cranes=sorted(cranes,key=lambda agv:agv.index)
        for t in range(max_time+1):
            for i in range(num_agvs-1):
                j=i+1
                dis=self.safe_distance
                x1=cranes[i].pos[t]
                x2=cranes[j].pos[t]
                if abs(x1-x2) < dis:
                    print(f'{cranes[i]}:{x1} hit {cranes[j]}:{x2}')
                    return False
                    #raise ValueError(f'{cache[i]} hit {cache[j]}')
        return True

    def reset(self):
        for m in self.machines.values():
            m.reset()
            
    @property
    def ends_of_machine_occupancies(self):
        num_machines=self.instance.num_machines
        rt=[0]*num_machines
        for i,m in self.machines.items():
            rt[i]=m.last_time
        return np.array(rt,dtype=float)

    def check_done(self) -> bool:
        rt=True
        for job in self.jobs.values():
            for task in job.tasks:
                if task.done==False:
                    rt=False
                    break
        return rt








 

 