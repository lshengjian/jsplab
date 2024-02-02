import itertools
from jsplab.core import Task
import numpy as np
def test_combination():
    data=list(itertools.product([0, 1], repeat=3))
    assert 8==len(data) and (0,0,0)==data[0] and   (1,1,1)==data[7]


def test_nonzero():
    idxs=np.nonzero([0,1.5,2])[0] #只有1维
    assert [1,2]==idxs.tolist()

def test_task():
    task=Task(job_index=0,task_index=0,machine_times=[0,1,1])
    msg=str(task)
    assert 'J1-1|1'==msg
    assert 'J1-1|1,[(2,1),(3,1)]'==task.str_info()
    task=Task(job_index=0,task_index=1,machine_times=[-1,3,20])
    msg=str(task)
    assert 'J1-2|20'==msg
    assert 'J1-2|20,[(2,3),(3,20)]'==task.str_info()