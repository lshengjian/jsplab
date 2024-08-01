
from __future__ import annotations
from typing import  List,Dict
from .machine import Machine,Tank,Transfer
from .crane import OverHeadCrane
from .instance import Instance
from .task import Task,extend_tasks
from ..datadef import G
from .job import Job
import numpy as np
class JobShop:
    def __init__(self,ins:Instance):
        # config = OmegaConf.load("conf/constant.yaml")
        # self.args:Constant = get_dataclass_by_name('Constant')(**config)
        self.instance:Instance =ins  

        self.machines:Dict[int,Machine]={}
        self.cranes:List[OverHeadCrane]=[]
        self.jobs:Dict[int,Job]={}
        self.machine_indexs_locked=set()
 
    def get_next_tasks(self):
        rt=[]
        for job in self.jobs.values():
            rt.append(job.cur_task if not job.cur_task.is_last else None)
        return rt
    def reset(self,job_nums_dict={}):
        self.machine_indexs_locked.clear()
        self.jobs.clear()
        tasks=extend_tasks(self.instance.tasks,job_nums_dict)
        self.instance.setup(tasks)
        if len(self.machines)<1:
            ins=self.instance
            for i in range(ins.num_machines):
                if i<ins.first_crane_index:
                    self.machines[i]=Tank(i,ins.machine_offsets[i],ins.machine_names[i])
                else:
                    if  isinstance(ins.machine_offsets[i],list):
                        self.machines[i]=Transfer(i,ins.machine_offsets[i],ins.machine_names[i])
                    else:
                        self.machines[i]=OverHeadCrane(i,ins.machine_offsets[i],ins.machine_names[i],ins.max_steps)
                        self.cranes.append(self.machines[i])

        else:
            for m in self.machines.values():
                m.reset()
        
        for task in tasks:
            if task.job_index not in self.jobs:
                self.jobs[task.job_index]=Job(task.job_index,task.proc_index)
            job=self.jobs[task.job_index]
            job.add_task(task)
        self.tasks=tasks

    def lock(self,tank:Machine):
        self.machine_indexs_locked.add(tank.index)
    def unlock(self,tank:Machine):
        self.machine_indexs_locked.remove(tank.index)
    def is_lock(self,tank_idx:int):
        return tank_idx in self.machine_indexs_locked
    def get_job_pos(self,step:int,job:Job)->int:
        #job:Job=self.jobs[job_index]
        data=sorted(job.tasks,key=lambda t:t.time_started)
        for task in data:
            if step<task.time_started and task.index==0:
                return -1
            if step<=task.time_finished:
                break
        # if step>task.time_finished:
        #     return -1
        if task.index%2==0 and not task.is_last:
            x= self.instance.machine_offsets[task.selected_machine]
            if isinstance(x,list):
                x=x[0] #todo
            return x
        for agv in self.cranes:
            if agv.index==task.selected_machine and not task.is_last:
                return agv.pos[step]
        return -1

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

    def choose_machine(self, task: Task) -> int:
        """
        This function performs the logic, with which the machine is chosen (in the case of the flexible JSSP)
        Implemented at the moment: Choose the machine out of the set of possible machines with the earliest possible
        start time

        :param task: Task

        :return: Machine on which the task will be scheduled.

        """
        possible_machines = task.machines
        for i,v in enumerate(possible_machines):
            if v>0 and self.is_lock(i):
                possible_machines[i]=0
        if sum(possible_machines)<1:
            #return -1
            raise ValueError(f'{task} not eligible_machines')
        machine_times = np.where(possible_machines,
                                 self.ends_of_machine_occupancies,
                                 np.full(len(possible_machines), np.inf))

        return int(np.argmin(machine_times)) #todo fix bug







 

 