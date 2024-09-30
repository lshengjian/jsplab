from jsplab.core import *
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

        self.jobs={}
        self.setup()

    def setup(self):
        '''
        0 1 2 3 4 5 6 7 8 9 0 T
        S     H   t1        1
                  t2    H   2
        3 2 1 0 9 8 7 6 5 4 3  
        E
        '''
        esper=self.world
        m=Machine(0,0,0)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,StartBuff())
        m=Machine(99,23,23)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,EndBuff())

        m=Machine(11,5,5)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,OpTank())
        m=Machine(12,18,18)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,OpTank())

        m=Machine(21,3,3)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,Hoist(),Moveable(0,10),Trajectory())
        m=Machine(22,15,15)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,Hoist(),Moveable(13,23),Trajectory())

        m=Machine(31,10,10)
        self.machines[m.id]=m
        self.machines_entity[m.id]=esper.create_entity(m,Moveable(10,13),Trajectory())

        self.world.add_processor(SysRecord())
        self.world.add_processor(SysMove(),priority=1)
        self.world.add_processor(SysDispatch(),priority=2)
        self.world.add_processor(SysPickup(),priority=1)
        self.world.add_processor(SysDropdown(),priority=1)
        self.world.add_processor(SysOperate(),priority=9)




        
        #self.jobs[0]=esper.create_entity(j1,j1_1)
    def put_job(self):
        esper=self.world
        start=self.machines_entity[0]
        esper.add_component(start,WithTask())
        logger.debug('add job')
        #(esper.components_for_entity(start))



    def on_arrived(self,move_ent:int,target:MoveTarget):
        
        data=self.world.try_component(move_ent,Hoist)
        m=self.world.try_component(move_ent,Machine)
        if data!=None:
            if self.world.has_component(move_ent,WithTask) and data.offset_y==2:
                self.world.add_component(move_ent,Dropdown())
                logger.info(f'{m} Dropdown')
            else:
                tank_ent:int=target.tank_ent
                #tank:Machine=self.world.component_for_entity(target_ent,Machine)
                if self.world.has_component(tank_ent,WithTask):
                    self.world.add_component(move_ent,Pickup())
                    logger.info(f'{m} Pickup')
                    task=self.world.component_for_entity(tank_ent,WithTask)
                    task.next_op_name='todo'
                    # todo edit task
                    self.world.remove_component(tank_ent,WithTask)
                    self.world.add_component(move_ent,task)
                

        #print(f"tran_arrived:{target.to_offset}")

    def dispaly(self,ent):
        for c in self.world.components_for_entity(ent):
            print(c)
        

    def play(self):
        t=0
        dt=1
        for i in range(20):
            t+=dt
            self.world.process(dt,t)
        self.dispaly(self.machines_entity[21])
