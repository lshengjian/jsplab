from jsplab.cbd import IState,FSM,Component,EventManager

class Transfer(Component):
    def __init__(self):
        super().__init__()
        self.center:EventManager=None
        self.x1:float=0
        self.x2:float=3
        self.x:float=0
        self.speed:float=1
        self.carring=None
        self.free_timer=0
        self.move_timer=0
    
    def update(self,delta_time:float=1,total_time=1):
        if self.carring is None:
            self.goto_target(self.x1,delta_time) 
        else:
            self.goto_target(self.x2,delta_time)
        if abs(self.x-self.x1)<1e-3 or abs(self.x-self.x2)<1e-3:
            self.free_timer+=delta_time
        else:
            self.move_timer+=delta_time

    def goto_target(self,tartget:float, delta_time:float):
        dis=abs(tartget-self.x)
        if dis>1e-2:
            dir1=tartget-self.x
            self.x+=self.speed*dir1/dis*delta_time
            dir2=tartget-self.x
            if dir1*dir2<=0:
                self.x=tartget
                if self.center!=None:
                    self.center.publish('on_transfer_arrived',self)



    