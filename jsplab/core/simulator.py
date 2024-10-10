from jsplab.core.components import *
from jsplab.core.systems import *
from jsplab.utils import World
import logging
logger = logging.getLogger(__name__.split('.')[-1])

class Simulator:
    def __init__(self):
        self.world=World()
        self.world.set_handler('on_arrived', self.on_arrived)
        #self.world.set_handler('on_end', self.dispaly)
        
        self.machines={}
        self.machines_entity={}

        #self.jobs={}
        self.setup()

    def schedule(self,task:Task)->Task:
        task.step_index+=1
        # todo
        return task

    def job_in_tank(self,task:Task,machine_ent:int,hoist_ent:int=-1):
        esper:World=self.world
        t:Task=esper.try_component(machine_ent,Task)
        m:Machine=esper.component_for_entity(machine_ent,Machine)
        if t!=None:
            raise ValueError(f'{m} alrady had a {t}, but you want put another {task}')
        if esper.has_component(machine_ent,Scheduled):
            esper.remove_component(machine_ent,Scheduled)
        if esper.has_component(machine_ent,Free):
            esper.remove_component(machine_ent,Free)
        esper.add_component(machine_ent,task)
        if hoist_ent>=0:
            esper.remove_component(hoist_ent,Task)
            
    def job_out_tank(self,task:Task,machine_ent:int,hoist_ent:int):
        esper:World=self.world
        t:Task=esper.try_component(machine_ent,Task)
        if t==None:
            m:Machine=esper.component_for_entity(machine_ent,Machine)
            logger.error(f'not task in {m},but you want pickup')
            return 
        esper.remove_component(machine_ent,Task)
        esper.add_component(machine_ent,Free())
        esper.add_component(hoist_ent,self.schedule(task))

            #esper.dispatch_event('on_plan',machine_ent,task)#在回调函数中更新到下一个任务
            

    def setup(self):
        '''
        0 1 2 3 4 5 6 7 8 9 0 T
        S     H   t1        1
                  t2    H   2
        3 2 1 0 9 8 7 6 5 4 3  
        E
        '''
        esper=self.world
        m=Machine(0,'S',0)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,Tank(),Free())
        m=Machine(99,'E',23)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,Tank(),Free())

        m=Machine(11,'t1',5)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,Tank(),Free())
        m=Machine(12,'t2',18)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,Tank(),Free())
        #print(self.machines_entity[m.id])
        m=Machine(31,'T',10)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,Transfer(),Movable(10,13,10),Free())

        
        m=Machine(21,'H1',3)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,Hoist(),Movable(0,10,3),Free(),Trajectory())
        # m=Machine(22,'H2',15)
        # self.machines[m.id]=m
        # self.machines_entity[m.id]=esper.create_entity(m,Hoist(),Movable(13,23,15),Free(),Trajectory())
 
  
        self.world.add_processor(SysOperate(),priority=9)
        self.world.add_processor(SysPickup(),priority=2)
        self.world.add_processor(SysDropdown(),priority=2)
        self.world.add_processor(SysMove(),priority=1)

        self.world.add_processor(SysDispatch())
 
        #self.world.add_processor(SysRecord())
      
    def put_job(self,task:Task=None):
        esper=self.world
        # start=self.machines_entity[31]
        # esper.add_component(start,)
        if task is None:
            task=Task()
        self.job_in_tank(task,self.machines_entity[0])
        logger.debug('add job')

    def on_arrived(self,ent,machine):
        #for c in self.world.components_for_entity(ent):
        print(f'{machine} arrived')
        

    def play(self):
        t=0
        dt=1
        for i in range(40):
            t+=dt
            self.world.process(dt,t)
            # for c in self.world.components_for_entity(self.machines_entity[0]):
            #     print(c)
        #self.dispaly(self.machines_entity[21])
