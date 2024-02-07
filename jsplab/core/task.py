"""This file provides the Task class."""

from typing import List,Dict
import numpy as np
from collections import defaultdict,namedtuple

__all__=[ 'defaultdict','namedtuple', 'OpTime','Task' ]

OpTime = namedtuple("OpTime", "machine duration")
# Point = namedtuple('Point', ['x', 'y'], defaults=(0.0, 0.0))
class Task:

    def __init__(self, job_index: int, task_index: int,
                 machine_times: List[int] = None,
                 deadline: int = 0, done: bool = False,
                 runtime: int = 0, started: int = 0, finished: int = 0, selected_machine: int = 0,
                 ):

        # test for correct data type of required and throw type error otherwise
        if not isinstance(job_index, int) or not isinstance(task_index, int):
            raise TypeError("Job index and task index must be of type int.")

        # public - static - required - don't touch after init
        self.job_index = job_index #作业索引号，从0开始
        self.task_index = task_index #任务索引号，从0开始

        # public - static - optional - don't touch after init
        
        self._machines = [] # like (1,0,1) 说明机器1和3能用
        self._runtimes = []
        self.machines = machine_times 
        #self.tools = tools       #可用工具集合
        self.deadline = deadline
        #self.instance_hash = instance_hash

        # public - non-static - optional
        self.done = done
        self.runtime = runtime
        self.started = started
        self.finished = finished
        self.selected_machine = selected_machine

        # protected - optional
        # self._n_machines = _n_machines
        # self._n_tools = _n_tools
        # self._feasible_machine_from_instance_init = _feasible_machine_from_instance_init
        # self._feasible_order_index_from_instance_init = _feasible_order_index_from_instance_init

    @property 
    def machines(self):
        times=self._runtimes
        data=np.where(times>0,np.ones_like(times),times)
        return data.tolist()
    
    @machines.setter
    def machines(self,op_times):
        data=np.array(op_times)
        times=np.where(data<0,np.zeros_like(data),data)
        self._runtimes=times
        self.runtime=max(times)

    def __str__(self) -> str:
        return f"J{self.job_index+1}-{self.task_index+1}|{self._runtimes}"

    def str_info(self) -> str:
        m_idxs=np.nonzero(self._runtimes)[0]

        ms=map(lambda idx:idx+1,m_idxs)
        ts=self._runtimes[m_idxs]

        data=str(list(zip(ms,ts))).replace(' ','')
        return f"J{self.job_index+1}-{self.task_index+1}|{self.runtime:.0f},{data}"
    
