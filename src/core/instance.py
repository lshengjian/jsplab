from .task import Task,OpTime,convert2fjsp_data
from typing import List,Tuple
from collections import defaultdict
import numpy as np

# def greedy_select(job:Job,ms:List[Machine]):
#     op_times=np.array(job.cur_task._runtimes)
#     op_times[op_times<1]=1e10
#     for i,t in enumerate(op_times):
#         op_times[i]=t*(1+ms[i].utilization_rate(job._last_time))
#     idxs=np.argsort(op_times)
#     job.assign(ms[idxs[0]])

class Instance:
    def __init__(self,name='',tasks:List[Task]=[], \
                offsets:List[int]=[],machine_names:List[str] =[], \
                first_crane_index:int=None
                ):
        self.name:str=name
        self.tasks:List[Task]=tasks
        self.machine_offsets:List[int]=offsets
        self.machine_names=machine_names
        if len(machine_names)<1:
            for m in range(len(self.machine_offsets)):
                self.machine_names.append(f'M{m+1}')
        else:
            assert len(machine_names)==len(offsets)

        self.first_crane_index:int=first_crane_index
        self.setup()
    
    # @property 
    # def world(self)->Tuple[List[Machine],List[Job]]:
    #     ms:List[Machine]=[]
    #     for m_id in range(self.num_machines):
    #         ms.append(Machine(m_id,self.machine_offsets[m_id]))

    #     job_dict={}
    #     for task in self.tasks:
    #         job=job_dict.get(task.job_index,None)
    #         if (job is None):
    #             job=Job(task.job_index)
    #             job_dict[job.index]=job
    #         job.add_task(task)
    #     return ms,job_dict.values()
    


    def setup(self):
        data=convert2fjsp_data(self.tasks)
        self.num_jobs = num_jobs=len(data)
        self.num_machines = num_machines=len(self.tasks[0].machines)
        max_alt_machines=0
        op_times=defaultdict(list)
        num_tasks_job={}
        #machines=list(range(self.num_machines))
        for j,job in enumerate(data):
            num_tasks_job[j]=0
            for t,task in enumerate(job):
                #print(task)
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
        first_task_index_job={0:0}
        for j in range(1,len(num_tasks_job)):
            last=first_task_index_job.get(j-1,0)
            first_task_index_job[j]=last+self.num_tasks_job[j-1]
        self.first_task_index_job=first_task_index_job

        
    def __str__(self) -> str:
        return f'{self.name}|{self.machine_offsets}|{self.first_crane_index}'
    
def get_max_steps(instance: Instance,crane_up_time=2,crane_down_time=2,scale=1):
    rt=0
    for task_id in range(len(instance.tasks)-1):
        if task_id%2==0:#加工型
            task=instance.tasks[task_id]
            rt+=task.runtime
            #print(task_id+1,task.runtime)
        else:
            pre=instance.tasks[task_id-1]
            next=instance.tasks[task_id+1]
            
            m1_idxs=pre.eligible_machines
            m2_idxs=next.eligible_machines

            x1=instance.machine_offsets[m1_idxs[0]]#上个电镀作业的第一个机器位置
            x2=instance.machine_offsets[m2_idxs[-1]]#下个电镀作业的最后一个机器位置
            dt=abs(x2-x1)+crane_up_time+crane_down_time# todo
            rt+=dt 
    task=instance.tasks[-1]#最后一个加工处理
    rt+=task.runtime
    return round(rt*scale)
