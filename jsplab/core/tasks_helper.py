"""This file provides the Task class."""

from typing import List,Dict
import numpy as np
from .task import *

__all__=['convert2jsp_data',
         'convert2fjsp_data',

         ]
def set_deadlines_to_max_deadline_per_job(instances: List[List[Task]]):
    """
    Equals all Task deadlines from one Job according to the one of the last task in the job

    :param instances: List of instances
    :param num_jobs: Number of jobs in an instance

    :return: List of instances with equaled job deadlines

    """
    # Argument sanity check
    # assert isinstance(instances, list) and isinstance(num_jobs, int), \
    #     "Warning: You can only set deadlines for a list of instances with num_jobs of type integer."

    for instance in instances:
        num_jobs=max([task.job_index for task in instance])+1
        # reset max deadlines for current instance
        max_deadline = [0] * num_jobs
        # get max deadline for every job
        for task in instance:
            if task.deadline > max_deadline[task.job_index]:
                max_deadline[task.job_index] = task.deadline
        # assign max deadline to every task
        for task in instance:
            task.deadline = max_deadline[task.job_index]

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

    job_data=defaultdict(list)
    task_data=defaultdict(list)

    for task in instance:
        times=task._runtimes
        m_idxs=np.nonzero(times)[0]
        
        for idx in m_idxs:
            task_data[task.job_index,task.task_index].append(OpTime(idx,times[idx]))
   
    for j_idx,t_idx  in  task_data.keys():
        job_data[j_idx].append(task_data[j_idx,t_idx])

    return list(job_data.values())