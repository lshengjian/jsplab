from .common import *
from .task import *
from typing import List

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