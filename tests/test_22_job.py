from src.core import  *

def test_job():
    paser:IParse=ExcelFileParser()
    info=paser.parse('fjsp/demo/3x3.xlsx')
    data=info.tasks
    assert 3==info.max_machines_per_task
    job=Job(0)
    for task in info.tasks:
        if task.job_index==0:
            job.add_task(task)

    assert 'J1[0.00] 1:5 2:6 3:3 '==str(job)
    ma=Machine()
    job.assign(ma)
    assert 'J1[0.25] 1:3 2:6 3:3 '==str(job)



    

    