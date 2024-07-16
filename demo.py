
from src.core import  *

def demo():
    paser:IParse=ExcelFileParser()
    info=paser.parse('fjsp/demo/3x3.xlsx')
    data=info.tasks
    assert 3==info.max_machines_per_task
    job=Job(0)
    for task in info.tasks:
        if task.job_index==0:
            job.add_task(task)
    print(job)
    ma=Machine()
    job.assign(ma)
    print(job)

if __name__ == '__main__':
    demo()

 