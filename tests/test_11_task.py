from src.core import Task

def test_task():
    task=Task(job_index=0,task_index=0,op_times=[0,1,1])
    msg=str(task)
    assert 'J1-1|1'==msg
    assert False==task.done
    assert 'J1-1|1,[(2,1),(3,1)]'==task.info()
    task=Task(job_index=0,task_index=1,op_times=[-1,3,20])
    msg=str(task)
    assert 'J1-2|20'==msg
    assert 'J1-2|20,[(2,3),(3,20)]'==task.info()

