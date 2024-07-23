# from src.core.advanced.machine import Machine,Tank,OverHeadCrane,MachineType
# from src.core import Job,Task
# import pytest
# def test_repeate_jobid():
#     j1=Job(0)
#     j2=Job(1)
#     assert len(Job.cache)==2
#     assert j1==Job.cache[0]
#     assert j2==Job.cache[1]
#     assert Job.cache[0]!=Job.cache[1]
#     with pytest.raises(ValueError) as e:
#         j2=Job(0)
#         assert str(e.value) == "already have a job with id=0"
#     Job.clean()
#     j3=Job(0)
#     assert len(Job.cache)==1
#     assert j3==Job.cache[0]
# def test_tank_and_crane():
#     Machine.clear()
#     job=Job(0)
#     t1=Tank(0,1,'除油1')
#     t2=Tank(1,2,'除油2')
#     t3=Tank(2,4,'水洗1')
#     t4=Tank(3,5,'水洗2')
#     h1=OverHeadCrane(4,3,'H1')
#     assert  h1==Machine.get_from_cache(4)
#     task1=Task(job.index,0,op_times=[10,10,0,0,0])
#     task2=Task(job.index,1,op_times=[0,0,0,0,1])
#     task3=Task(job.index,2,op_times=[0,0,5,5,0])
#     job.add_task(task1)
#     job.add_task(task2)
#     job.add_task(task3)
#     assert 0==job.cur_task_index
#     job.assign(t1)
#     assert job._last_time==10
#     assert task1.selected_machine==t1.index
#     assert 1==job.cur_task_index
#     job.assign(h1,t4)
#     assert job._last_time==10+(5-1)+2+2

# # def test_job():
# #     paser:IParse=ExcelFileParser()
# #     info=paser.parse('fjsp/demo/3x3.xlsx')
# #     data=info.tasks
# #     assert 3==info.max_machines_per_task
# #     job=Job(0)
# #     for task in info.tasks:
# #         if task.job_index==0:
# #             job.add_task(task)

# #     assert 'J1[0.00] 1:5 2:6 3:3 '==str(job)
# #     ma=Machine()
# #     job.assign(ma)
# #     assert 'J1[0.25] 1:3 2:6 3:3 '==str(job)



    

    