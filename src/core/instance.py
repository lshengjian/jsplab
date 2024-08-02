from .task import Task,OpTime,convert2fjsp_data
from typing import List
from collections import defaultdict
import numpy as np
from ..datadef import G

# def greedy_select(job:Job,ms:List[Machine]):
#     op_times=np.array(job.cur_task._runtimes)
#     op_times[op_times<1]=1e10
#     for i,t in enumerate(op_times):
#         op_times[i]=t*(1+ms[i].utilization_rate(job._last_time))
#     idxs=np.argsort(op_times)
#     job.assign(ms[idxs[0]])

class Instance:
    '''
    这里的tasks中的每个均是任务模板,后续可以复制多个类似的task
    '''
    def __init__(self,name='',tasks:List[Task]=[], \
                offsets:List[int]=[],machine_names:List[str] =[], \
                first_crane_index:int=None
                ):
        self.name:str=name
        self.tasks:List[Task]=tasks
        self.machine_offsets:List[int]=offsets
        self.num_machines = len(self.tasks[0].machines)

        product_ids=set(map(lambda t:t.product_index,tasks))
        self.product_ids=product_ids
        xs=[]
        for x in offsets:
            if isinstance(x,list):#Transfer had 2 offsets [ x1,x2 ]
                xs.extend(x)
            else:
                xs.append(x)
        self.min_offset=min(xs)
        self.max_offset=max(xs)

        self.machine_names=machine_names
        if len(machine_names)<1:
            for m in range(len(self.machine_offsets)):
                self.machine_names.append(f'M{m+1}')
        else:
            assert len(machine_names)==len(offsets)

        self.first_crane_index:int=first_crane_index
        self.setup(self.tasks)


    def setup(self,tasks:List[Task]):
        data=convert2fjsp_data(tasks)
        self.num_jobs = len(data)
        
        max_alt_machines=0
        op_times=defaultdict(list)
        num_tasks_job={}

        for j,job in enumerate(data):
            num_tasks_job[j]=0
            for t,task in enumerate(job):
                if max_alt_machines<len(task):
                    max_alt_machines=len(task)
                k=j,t
                num_tasks_job[j]+=1
                for alt in task:
                    op_times[k].append(OpTime(*alt))
        
        self.num_tasks_per_job=num_tasks_job
        self.max_tasks_per_job=max(num_tasks_job)
        num_tasks_job=list(num_tasks_job.values())
        self.op_times=op_times
        self.max_machines_per_task=max_alt_machines#每个任务最大处理机器数
        self.max_runtime=0
        job_seq_tasks=[]

        for j,size in enumerate(num_tasks_job):
            job_seq_tasks+=[j]*size
  
        self.job_seq_tasks=np.array(job_seq_tasks,dtype=int)#任务的作业编号的序列，用于遗传算法等
        self.num_total_tasks=len(job_seq_tasks)
        first_task_index_job={0:0}
        for j in range(1,len(num_tasks_job)):
            last=first_task_index_job.get(j-1,0)
            first_task_index_job[j]=last+self.num_tasks_per_job[j-1]
        self.first_task_index_job=first_task_index_job
        
        self.max_steps=get_max_steps(self,G.CRANE_UP_TIME,G.CRANE_DOWN_TIME,G.MAX_STEP_SCALE)

        
    def __str__(self) -> str:
        return f'{self.name}|{self.machine_offsets}|{self.first_crane_index}'



def get_max_steps(instance: Instance,crane_up_time=2,crane_down_time=2,scale=1):
    rt=0
    for task in instance.tasks:
        if task.index%2==0:
            rt+=task.runtime
            if instance.max_runtime<task.runtime:
                instance.max_runtime=task.runtime
        else:#天车处理任务
            pre=instance.tasks[task.index-1]
            next=instance.tasks[task.index+1]
            
            m1_idxs=pre.eligible_machines
            m2_idxs=next.eligible_machines

            x1=instance.machine_offsets[m1_idxs[0]]#上个电镀作业的第一个机器位置
            x2=instance.machine_offsets[m2_idxs[-1]]#下个电镀作业的最后一个机器位置
            if isinstance(x1,list):
                x1=x1[0]
            if isinstance(x2,list):
                x2=x2[-1]
            dt=abs(x2-x1)+crane_up_time+crane_down_time# todo
            task.runtime=dt
            rt+=dt
            if instance.max_runtime<dt:
                instance.max_runtime=dt
    return round(rt*scale)
