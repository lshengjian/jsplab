from jsplab.cbd import IState,FSM,Component,EventManager
from dataclasses import dataclass
from jsplab.conf import G,HoistPos
from .job import Job
import logging
logger = logging.getLogger(__name__.split('.')[-1])

@dataclass
class ShiftCommand:
    tank_index:int=0
    target:float=0
@dataclass
class TransportCommand:
    tank1_index:int=0
    tank2_index:int=0
    tank1_offset:float=0
    tank2_offset:float=0
    urgency:int =0
    job_index:int=0
    def __str__(self):
        return f"J{self.job_index+1} {self.tank1_offset}->{self.tank2_offset}"
        

    
class Hoist(Component):
    def __init__(self):
        super().__init__()
        self.code='H1'
        self.center:EventManager=None
        self.fsm:FSM=FSM()
        self.x:float=0
        self.y:float=0
        self.min_x:float=0
        self.max_x:float=0
        #self.dx:float=0

        self.speed:float=1
        self.speed_y:float=0.25
        self.carring:Job=None
        self.working_time=0
        self.free_time=0
        self.cmd=None
    def __str__(self):
        return f"{self.code}|{self.x:02.0f}"
    def update(self,delta_time:float,total_time):
        self.fsm.update(delta_time,total_time)
        
        if isinstance(self.fsm.current_state,FreeState):
            self.free_time+=delta_time
        else:
            self.working_time+=delta_time
        if self.carring!=None:
            self.carring.x=self.x
            self.carring.y=self.y

class HoistRecord(Component):
    def __init__(self):
        super().__init__()
        #self.last_x:int=None
        self.steps={}
        
    def update(self,delta_time:float,total_time):
        self._hoist=self.game_object.get_component(Hoist)
        if len(self.steps)<1:
            self.steps[0]=self._hoist.x
        ts=list(self.steps.keys())
        last_x=self.steps[ts[-1]]
        if abs(last_x-self._hoist.x)>0.9:
            self.steps[round(total_time)]=self._hoist.x
            msg=f'{str(self._hoist)}'
            logger.info(msg)
class FreeState(IState):
    def __init__(self,h: Hoist):
        self.hoist: Hoist=h
    def enter(self):
        self.hoist.cmd=None
        #self.hoist.dx=0
        msg=f'{self.hoist.code} enter FreeState'
        logger.debug(msg)
    def exit(self):
        pass
        #print('exit FreeState')
    def update(self,delta_time:float,total_time):
        if self.hoist.cmd!=None:
            self.hoist.fsm.set_state('MovingState')
        
        

class LiftingState(IState):
    def __init__(self,h: Hoist):
        self.hoist: Hoist=h
    def enter(self):
        if self.hoist.center!=None:
            self.hoist.center.publish('on_hoist_pickup',self.hoist)
        #print('enter LiftingState')
    def exit(self):
        pass

    def update(self,delta_time:float,total_time):
        self.hoist.y+=delta_time*self.hoist.speed_y

        if self.hoist.y>=2:
            self.hoist.y=2
            # if self.hoist.center!=None:
            #     self.hoist.center.publish('on_hoist_at_top',self.hoist)
            self.hoist.fsm.set_state('MovingState')

class LoweringState(IState):
    def __init__(self,h: Hoist):
        self.hoist: Hoist=h

    def enter(self):
        pass
        #print('enter LoweringState')
    def exit(self):
        pass
        # if self.hoist.center!=None:
        #     self.hoist.center.publish('on_hoist_drop',self.hoist)
    def update(self,delta_time:float,total_time):
        self.hoist.y-=delta_time*self.hoist.speed_y
        if self.hoist.y<=0:
            self.hoist.y=0
            if self.hoist.center!=None:
                self.hoist.center.publish('on_hoist_drop',self.hoist,self.hoist.carring)
            self.hoist.cmd=None
            self.hoist.fsm.set_state('FreeState')

class MovingState(IState):
    def __init__(self,h: Hoist):
        self.hoist: Hoist=h
        self.target=None

    def enter(self):
        
        target=None
        if isinstance(self.hoist.cmd,ShiftCommand):
            target=self.hoist.cmd.target
            
        elif isinstance(self.hoist.cmd,TransportCommand):
            if abs(self.hoist.cmd.tank1_offset-self.hoist.x)<G.EPS and abs(self.hoist.y-2)<G.EPS:
                target=self.hoist.cmd.tank2_offset
            else:
                target=self.hoist.cmd.tank1_offset
        self.target=target

        #self.hoist.dx=1 if target>self.hoist.x else -1

    def exit(self):
        self.target=None


    def update(self,delta_time:float,total_time):
        target=self.target
        dis=abs(target-self.hoist.x)
        if dis>G.EPS:
            dir1=target-self.hoist.x
            self.hoist.x+=self.hoist.speed*dir1/dis*delta_time
            dir2=target-self.hoist.x
            if dir1*dir2<=0:
                self.hoist.x=target
        
        dis=abs(target-self.hoist.x)
        if dis<=G.EPS:
            if isinstance(self.hoist.cmd,ShiftCommand):
                self.hoist.fsm.set_state('FreeState')
            elif isinstance(self.hoist.cmd,TransportCommand):
                if abs(self.hoist.y-2)<G.EPS and abs(self.hoist.cmd.tank2_offset-self.hoist.x)<G.EPS:
                    self.hoist.fsm.set_state('LoweringState')
                else:
                    self.hoist.fsm.set_state('LiftingState') 
