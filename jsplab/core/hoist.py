from jsplab.cbd import IState,FSM,Component,EventManager
from dataclasses import dataclass
from jsplab.conf import G
@dataclass
class ShiftCommand:
    target:float=0
@dataclass
class TransportCommand:
    tank1_offset:float=0
    tank2_offset:float=0
    urgency:int =0

class Hoist(Component):
    def __init__(self):
        super().__init__()
        self.code='H1'
        self.center:EventManager=None
        self.fsm:FSM=FSM()
        self.x:float=0
        self.y:float=0
        self.dx:float=0

        self.speed:float=1
        self.speed_y:float=0.25
        self.carring=None
        self.working_time=0
        self.free_time=0
        self.cmd=None

    def update(self,delta_time:float,total_time):
        self.fsm.update(delta_time,total_time)
        if isinstance(self.fsm.current_state,FreeState):
            self.free_time+=delta_time
        else:
            self.working_time+=delta_time


class FreeState(IState):
    def __init__(self,h: Hoist):
        self.hoist: Hoist=h
    def enter(self):
        self.hoist.cmd=None
        self.hoist.dx=0
        print(f'{self.hoist.code} enter FreeState')
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
        pass
        #print('enter LiftingState')
    def exit(self):
        pass
        #print('exit LiftingState')
    def update(self,delta_time:float,total_time):
        self.hoist.y+=delta_time*self.hoist.speed_y

        if self.hoist.y>=2:
            self.hoist.y=2
            if self.hoist.center!=None:
                self.hoist.center.publish('on_hoist_at_top',self)
            self.hoist.fsm.set_state('MovingState')

class LoweringState(IState):
    def __init__(self,h: Hoist):
        self.hoist: Hoist=h

    def enter(self):
        pass
        #print('enter LoweringState')
    def exit(self):
        pass
    def update(self,delta_time:float,total_time):
        self.hoist.y-=delta_time*self.hoist.speed_y
        if self.hoist.y<=0:
            self.hoist.y=0
            if self.hoist.center!=None:
                self.hoist.center.publish('on_hoist_at_bottom',self)
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
        self.hoist.dx=1 if target>self.hoist.x else -1

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
                if isinstance(self.hoist.cmd,ShiftCommand):
                    self.hoist.fsm.set_state('FreeState')
                elif isinstance(self.hoist.cmd,TransportCommand):
                    if abs(self.hoist.y-2)<G.EPS and abs(self.hoist.cmd.tank2_offset-self.hoist.x)<G.EPS:
                        self.hoist.fsm.set_state('LoweringState')
                    else:
                       self.hoist.fsm.set_state('LiftingState') 
