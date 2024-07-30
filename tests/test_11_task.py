from src.core import Task,extend_tasks

def test_task():
    task=Task(job_index=0,task_index=0,op_times=[0,1,1])
    msg=str(task)
    assert 'J1-1|1'==msg
    assert False==task.done
    assert 'J1-1|1,[(2,1),(3,1)]'==task.info
    task=Task(job_index=0,task_index=1,op_times=[-1,3,20])
    msg=str(task)
    assert 'J1-2|20'==msg
    assert 'J1-2|20,[(2,3),(3,20)]'==task.info

def test_extend():
    t11=Task(job_index=0,task_index=0,op_times=[1,1,0])
    t12=Task(job_index=0,task_index=1,op_times=[0,2,2])
    t21=Task(job_index=1,task_index=0,op_times=[1,1,1])
    job_nums={0:2,1:3}
    tasks=extend_tasks([t11,t12,t21],job_nums)
    assert 7==len(tasks) 
    assert tasks[0].job_index==0 and tasks[0].index==0 and list(tasks[0].machines)==[1,1,0]
    assert tasks[1].job_index==0 and tasks[1].index==1 and list(tasks[1].machines)==[0,1,1] and list(tasks[1]._runtimes)==[0,2,2]
    assert tasks[2].job_index==1 and tasks[2].index==0 and list(tasks[2].machines)==[1,1,0]
    assert tasks[3].job_index==1 and tasks[3].index==1 and list(tasks[3].machines)==[0,1,1] and list(tasks[3]._runtimes)==[0,2,2]
    assert tasks[4].job_index==2 and tasks[4].index==0 and list(tasks[4].machines)==[1,1,1]
    assert tasks[5].job_index==3 and tasks[5].index==0 and list(tasks[5].machines)==[1,1,1] 
    assert tasks[6].job_index==4 and tasks[6].index==0 and list(tasks[6].machines)==[1,1,1]
    