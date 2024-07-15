from typing import List,Dict
import numpy as np
from collections import namedtuple,defaultdict

__all__=[  'OpTime','Task','convert2jsp_data','convert2fjsp_data' ]

OpTime = namedtuple("OpTime", "machine duration")
# Point = namedtuple('Point', ['x', 'y'], defaults=(0.0, 0.0))
class Task:
    def __init__(self, job_index: int, task_index: int,
                 op_times: List[int] = None,
                 runtime: int = -1, started: int = -1, finished: int = 0, selected_machine: int = -1,
                 ):

        # test for correct data type of required and throw type error otherwise
        if not isinstance(job_index, int) or not isinstance(task_index, int):
            raise TypeError("Job index and task index must be of type int.")
        # public - static - required - don't touch after init
        self.job_index = job_index #作业索引号，从0开始
        self.task_index = task_index #任务索引号，从0开始



        # public - non-static - optional
        self.runtime = runtime  #没有开始前存可能的最长加工时间，开始时记录实际加工的时间
        self.started = started
        self.finished = finished
        self.selected_machine = selected_machine

        # public - static - optional - don't touch after init
        #self._machine_masks = [] # like (1,0,1) 说明机器1和3能用
        self._runtimes = [] #保存每个机器的实际加工时间
        self.machines = op_times 

    @property 
    def machines(self):
        times=self._runtimes
        self.runtime=max(times)
        data=np.where(times>0,np.ones_like(times),times)
        
        return data.tolist()
    
    @machines.setter
    def machines(self,op_times):
        data=np.array(op_times)
        times=np.where(data<0,np.zeros_like(data),data)
        self._runtimes=times
        self.runtime=max(times)

    def __str__(self) -> str:
        return f"J{self.job_index+1}-{self.task_index+1}|{self.runtime}"

    def debug_info(self) -> str:
        m_idxs=np.nonzero(self._runtimes)[0]
        ms=map(lambda idx:idx+1,m_idxs)
        ts=self._runtimes[m_idxs]
        data=str(list(zip(ms,ts))).replace(' ','')
        return f"J{self.job_index+1}-{self.task_index+1}|{self.runtime:.0f},{data}"

def instance2dict(instance:List[Task])->Dict[int,List[List[OpTime]]]:
    job_data=defaultdict(list)
    task_data=defaultdict(list)

    for task in instance:
        times=task._runtimes
        m_idxs=np.nonzero(times)[0]
        for idx in m_idxs:
            task_data[task.job_index,task.task_index].append(OpTime(idx,times[idx]))
   
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