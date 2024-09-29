from jsplab.core import *
from jsplab.utils import World
class Simulator:
    def __init__(self):
        self.world=World()
        self.world.set_handler('on_arrived', self.tran_arrived)
        #self.world.set_handler('on_end', self.dispaly)
        
        self.machines={}
        self.jobs={}
        self.setup()

    def setup(self):
        '''
        0 1 2 3 4 5 6 7 8 9 0 T
        S     H   t1t2      1
                  t4t3  H   2
        3 2 1 0 9 8 7 6 5 4 3  
        E
        '''
        esper=self.world
        self.machines[0]=esper.create_entity(Machine(0))
        self.machines[1]=esper.create_entity(Machine(1,23,23))

        self.machines[11]=esper.create_entity(Machine(11,5,5))
        self.machines[12]=esper.create_entity(Machine(12,6,6))
        self.machines[13]=esper.create_entity(Machine(13,17,17))
        self.machines[14]=esper.create_entity(Machine(14,18,18))

        self.machines[21]=esper.create_entity(Machine(21,3,3),Moveable(0,10),CanUpDown(),Trajectory())
        self.machines[22]=esper.create_entity(Machine(22,15,15),Moveable(13,23),CanUpDown(),Trajectory())

        self.machines[31]=esper.create_entity(Machine(31,10,10),Moveable(10,13),Trajectory())
        self.world.add_processor(SysRecord())
        self.world.add_processor(SysMove(),priority=1)
        self.world.add_processor(SysDispatch(),priority=2)




        
        #self.jobs[0]=esper.create_entity(j1,j1_1)
    def put_job(self):
        esper=self.world
        start=self.machines[0]
        esper.add_component(start,Job(0,'A',2))
        esper.add_component(start,Task([5,6]))
        print(esper.components_for_entity(start))



    def tran_arrived(self,ent,t):
        print(f"tran_arrived:{t.to_offset}")

    def dispaly(self,ent):
        rt:Trajectory=self.world.component_for_entity(ent,Trajectory)
        print(rt.history)
        

    def play(self):
        t=0
        dt=1
        for i in range(20):
            t+=dt
            self.world.process(dt,t)
