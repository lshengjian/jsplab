from .task import Task,OpTime,convert2fjsp_data
from typing import List,Dict
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
        xs=[]
        for x in offsets:
            if isinstance(x,list):#对于转运机器，其有两个固定位
                xs.extend(x)
            else:
                xs.append(x)
        self.min_offset=min(xs)
        self.max_offset=max(xs)

        self.machine_names=machine_names
        if len(machine_names)<1:#没有机器名称
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
        
        self.num_tasks_job=num_tasks_job#每个作业有几个任务
        num_tasks_job=list(num_tasks_job.values())
        self.op_times=op_times
        self.max_machines_per_task=max_alt_machines#每个任务最大处理机器数
        
        job_seq_tasks=[]

        for j,size in enumerate(num_tasks_job):
            job_seq_tasks+=[j]*size
  
        self.job_seq_tasks=np.array(job_seq_tasks,dtype=int)#任务的作业编号的序列，用于遗传算法等
        self.num_tasks=len(job_seq_tasks)
        first_task_index_job={0:0}
        for j in range(1,len(num_tasks_job)):
            last=first_task_index_job.get(j-1,0)
            first_task_index_job[j]=last+self.num_tasks_job[j-1]
        self.first_task_index_job=first_task_index_job
        self.max_steps=get_max_steps(self)

        
    def __str__(self) -> str:
        return f'{self.name}|{self.machine_offsets}|{self.first_crane_index}'



def get_max_steps(instance: Instance,crane_up_time=2,crane_down_time=2,scale=1):
    rt=0
    for task_id in range(len(instance.tasks)-1):
        task=instance.tasks[task_id]
        if task_id%2==0:
            
            rt+=task.runtime
            #print(task_id+1,task.runtime)
        else:#天车处理任务
            pre=instance.tasks[task_id-1]
            next=instance.tasks[task_id+1]
            
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
    task=instance.tasks[-1]#最后一个加工处理
    rt+=task.runtime
    return round(rt*scale)
