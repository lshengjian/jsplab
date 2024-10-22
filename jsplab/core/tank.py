from jsplab.cbd import Component,EventManager
from jsplab.conf import G
from .workpiece import Job
class Tank(Component):
    def __init__(self):
        super().__init__()
        self.slot=0 #槽位号
        self.center:EventManager=None
        self.x:float=0 #本区段的偏移距离
        self.carring:Job=None
        self.free_time:float=0
        self.working_time:float=0
        self.timer:float=0
        self.plan_hoist=None

    def __str__(self):
        return f"T{self.slot}"
    
    def put_job(self,job:Job):
        self.carring=job
        self.timer=0
        self.plan_hoist=None

    def pop_job(self)->Job:
        job=self.carring
        self.carring=None
        self.plan_hoist=None
        return job
    
    def update(self,delta_time:float,total_time):
        job=self.carring
        if job is None:
            self.free_time+=delta_time
        else:
            self.working_time+=delta_time
            self.timer+=delta_time
            if job.cur_task :
                if self.timer>=job.cur_task.max_time:
                    print(f'{self} is Over !')
                    if self.center!=None:
                        self.center.publish('on_timeout',self)
                elif self.timer>=job.cur_task.min_time-3 and self.plan_hoist is None:
                    if self.center!=None:
                        self.center.publish('on_scheduling',self)
                    # print(f'{self} op finished!')
                    # self.plan_hoist=True

