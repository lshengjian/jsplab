from jsplab.cbd import IState,FSM,Component,EventManager

class Hoist(Component):
    def __init__(self):
        super().__init__()
        self.center:EventManager=None
        self.fsm=FSM()
        self.x:float=0
        self.y:float=0

        self.speed:float=1
        self.speed_y:float=0.25
        self.carring=None
        self.work_time=0

class FreeState(IState):
    def __init__(self):
        self.timer:float=0
    def enter(self):
        pass
    def exit(self):
        pass
    def update(self,delta_time:float,total_time):
        self.timer+=delta_time

class LiftState(IState):
    def __init__(self,h: Hoist):
        self.hoist: Hoist=h

    def enter(self):
        pass
    def exit(self):
        pass
    def update(self,delta_time:float,total_time):
        self.hoist.y+=delta_time*self.hoist.speed_y
        self.work_time+=delta_time
        if self.hoist.y>=2:
            self.hoist.y=2
            self.hoist.fsm.set_state('MoveState')
class DropState(IState):
    def __init__(self,h: Hoist):
        self.hoist: Hoist=h

    def enter(self):
        pass
    def exit(self):
        pass
    def update(self,delta_time:float,total_time):
        self.hoist.y-=delta_time*self.hoist.speed_y
        self.work_time+=delta_time
        if self.hoist.y<=0:
            self.hoist.y=0
            self.hoist.fsm.set_state('FreeState')
class MoveState(IState):
    def __init__(self,h: Hoist):
        self.hoist: Hoist=h
        self.target:float=None
    def enter(self):
        assert self.target is not None
    def exit(self):
        self.target=None
    def update(self,delta_time:float,total_time):
        target=self.target
        dis=abs(target-self.x)
        self.work_time+=delta_time
        if dis>1e-2:
            dir1=target-self.x
            self.x+=self.hoist.speed*dir1/dis*delta_time
            dir2=target-self.x
            if dir1*dir2<=0:
                self.x=target
                # if self.center!=None:
                #     self.center.publish('on_arrived',self)