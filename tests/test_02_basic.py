import itertools
from src.core import Task
from src.utils.common import get_agv_flags
import numpy as np

def test_combination():
    data=list(itertools.product([0, 1], repeat=3))
    assert 8==len(data) and (0,0,0)==data[0] and   (1,1,1)==data[7]


def test_nonzero():
    idxs=np.nonzero([0,1.5,2])[0] #只有1维
    assert [1,2]==idxs.tolist()

def test_task():
    task=Task(job_index=0,task_index=0,op_times=[0,1,1])
    msg=str(task)
    assert 'J1-1|1'==msg
    assert 'J1-1|1,[(2,1),(3,1)]'==task.debug_info()
    task=Task(job_index=0,task_index=1,op_times=[-1,3,20])
    msg=str(task)
    assert 'J1-2|20'==msg
    assert 'J1-2|20,[(2,3),(3,20)]'==task.debug_info()

def test_agv_move():
    #time   0   1   2   3   4   5   6   7   8   9   0   1   2   3   4
    pos   =[3,  2,  1,  0,  0,  0,  1,  2,  3,  4,  4,  4,  3,  3,  3]
    #step1 '←','←','←','o','o','→','→','→','→','o','o','←','o','o','o'
    #step2 '←','←','←','↑','↑','→','→','→','→','↓','↓','←','o','o','o'

    info=get_agv_flags(pos,[(3,11)])
    info=list(map(str,info))
    assert info==['←', '←', '←', '↑', '↑', '→', '→', '→', '→', '↓', '↓', '←', 'o', 'o', 'o']