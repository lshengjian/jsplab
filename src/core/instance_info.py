from .task import Task,convert2fjsp_data,OpTime
from typing import Tuple,List,Dict
from collections import defaultdict
import numpy as np
class InstanceInfo:
    def __init__(self,name='',jobs:List[Task]=[], \
                 offsets:List[int]=[],first_agv_index:int=None):
        self.name:str=name
        self.jobs:List[Task]=jobs
        self.machine_offsets:List[int]=offsets
        self.first_agv_index:int=first_agv_index
        self.setup()
    # def convert2ortools(self):
    #     return convert2fjsp_data(self.jobs)
    
    def setup(self):
        data=convert2fjsp_data(self.jobs)
        self.num_jobs = num_jobs=len(data)
        self.num_machines = num_machines=len(self.jobs[0].machines)
        max_alt_machines=0
        op_times=defaultdict(list)
        num_tasks_job={}
        ms=list(range(self.num_machines))
        for j,job in enumerate(data):
            num_tasks_job[j]=0
            for t,task in enumerate(job):
                if max_alt_machines<len(task):
                    max_alt_machines=len(task)
                k=j,t
                num_tasks_job[j]+=1
                for alt in task:
                    op_times[k].append(OpTime(*alt))
        
        self.num_tasks_job=num_tasks_job
        num_tasks_job=list(num_tasks_job.values())
        self.op_times=op_times
        self.max_machines_per_task=max_alt_machines
        
        job_seq_tasks=[]

        for j,size in enumerate(num_tasks_job):
            job_seq_tasks+=[j]*size
  
        self.job_seq_tasks=np.array(job_seq_tasks,dtype=int)
        self.num_tasks=len(job_seq_tasks)
        start_task_job={0:0}
        for j in range(1,len(num_tasks_job)):
            last=start_task_job.get(j-1,0)
            start_task_job[j]=last+self.num_tasks_job[j-1]
        self.start_task_job=start_task_job

        
    def __str__(self) -> str:
        return f'{self.name}|{self.machine_offsets}|{self.first_agv_index}'