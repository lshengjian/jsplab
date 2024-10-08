from typing import List,Dict
from numpy.typing import NDArray
import numpy as np
from collections import namedtuple,defaultdict

__all__=[  'OpTime','Task','extend_tasks','convert2jsp_data','convert2fjsp_data' ]

OpTime = namedtuple("OpTime", "machine duration")
# Point = namedtuple('Point', ['x', 'y'], defaults=(0.0, 0.0))
class Task:
    def __init__(self, job_index: int, task_index: int,op_times: List[int] = None
                ):

        # test for correct data type of required and throw type error otherwise
        if not isinstance(job_index, int) or not isinstance(task_index, int):
            raise TypeError("Job index and task index must be of type int.")
        # if job_index<product_index:
        #     raise ValueError("Job index {job_index} should greater product index  {product_index}")

        # optional
        #self.product_index=product_index
        self.is_last=False
        self.runtime = 0  #没有开始前存可能的最长加工时间，开始时记录实际加工的时间
        self.time_started = -1
        self.time_finished = -1
        self.selected_machine = -1
        self.done=False        
        # required - don't touch after init
        
        self.job_index = job_index #作业索引号，从0开始
        self.index = task_index #作业中的任务索引号，从0开始
        self._runtimes = [] #保存每个机器的实际加工时间
        self.machines = op_times 



    @property 
    def machines(self)->NDArray:
        times=self._runtimes
        data=np.where(times>0,np.ones_like(times),times)
        return data
    
    @machines.setter
    def machines(self,op_times:List[int]):
        data=np.array(op_times)
        times=np.where(data<0,np.zeros_like(data),data)
        self._runtimes=times
        self.runtime=max(times)
        self.eligible_machines=np.nonzero(times)[0] #only one dim
        #np.argwhere(times>0).flatten()

    def __str__(self) -> str:
        tag=f'J{self.job_index+1}-{self.index+1}|'
        msg1=f'{tag}{self.runtime}'
        msg2=f'{tag}{self.time_started}->{self.time_finished}'
        return msg2 if self.done else msg1

    @property
    def info(self) -> str:
        m_idxs=self.eligible_machines
        ms=map(lambda idx:idx+1,m_idxs)
        ts=self._runtimes[m_idxs]
        data=str(list(zip(ms,ts))).replace(' ','')
        return f"J{self.job_index+1}-{self.index+1}|{self.runtime:.0f},{data}"
    
def extend_tasks(tasks:List[Task],nums:Dict[int,int]={}):
    '''
    通过流程模板创建多个具体作业流程
    '''
    proc_ids=set(map(lambda task:task.job_index,tasks))
    product_tasks={p_id:list(filter(lambda task:task.job_index==p_id,tasks)) for p_id in proc_ids}
    
    cnt=0
    rt:List[Task]=[]
    for j_id,tasks in product_tasks.items():
        num_jobs=nums.get(j_id,1)
        for _ in range(num_jobs):
            for task in tasks:
                t2=Task(cnt,task.index,task._runtimes) 
                rt.append(t2)
            cnt+=1
    return rt
def instance2dict(instance:List[Task])->Dict[int,List[List[OpTime]]]:
    job_data=defaultdict(list)
    task_data=defaultdict(list)

    for task in instance:
        times=task._runtimes
        m_idxs=np.nonzero(times)[0]
        for idx in m_idxs:
            task_data[task.job_index,task.index].append(OpTime(idx,times[idx]))
   
    for j_idx,t_idx  in  task_data.keys():
        job_data[j_idx].append(task_data[j_idx,t_idx])
    return job_data  
 
def convert2fjsp_data(instance:List[Task])->List[List[List[OpTime]]]:
    """Convert instance to or-tools flex jobshop problem format.
    jobs = [  # task = (machine_id,processing_time )
        [  # Job 0
            [(0,3), (1,1), (2,5)], # task 0 with 3 alternatives
            [(2,0), (1,4), (2,6)],  # task 1 with 3 alternatives
         ],
        [  # Job 1
            [(0,2), (1,3), (2,4)]
        ]
    ]
    """
    data=instance2dict(instance)
    return list(data.values())

def convert2jsp_data(instance:List[Task])->List[List[OpTime]]:
    """Convert instance to or-tools minimal jobshop problem format.
    jobs_data = [  # task = (machine_id, processing_time).
        [(0, 3), (1, 2), (2, 2)],  # Job0
        [(0, 2), (2, 1), (1, 4)],  # Job1
        [(1, 4), (2, 3)],  # Job2
    ]
    """
    jobs_data:Dict[int,List[OpTime]]=defaultdict(list)
    for task in instance:
        times=task._runtimes
        m_idx=np.nonzero(times)[0][0]
        jobs_data[task.job_index].append(OpTime(m_idx,times[m_idx]))
    return list(jobs_data.values())