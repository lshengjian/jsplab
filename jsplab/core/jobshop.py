#   0   1   2   3   4   5   6   7   8   9
#   S|E             X   X           Y   Y
#   |<----------T0----->|
#                   |<------T1--------->|
#   pos(T1)>=pos(T0)+2
from jsplab.core import *
from jsplab.cbd import GameObject,EventManager
from typing import List,Union
import logging,math,random
from pyglet.shapes import Circle,BorderedRectangle
logger = logging.getLogger(__name__.split('.')[-1])

class JobShop:
    def __init__(self,num_hoists=2,num_jobs=2,offsets=None,steps=None):
        if offsets is None:
           offsets=[0,4,5,8,9]
           steps=[[4,5],[8,9],[4,5],[0]] 
        self.num_hoists=num_hoists
        self.num_jobs=num_jobs
        self.offsets=offsets
        self.steps=steps
        self.center=EventManager()
        

        self.reset()

    def exe(self,hoist_id,cmd:Union[ShiftCommand,TransportCommand]):
        self.hoists[hoist_id].cmd=cmd

    def reset(self):
        self.is_over=False
        self.sprites=[]
        self.hoists:List[Hoist]=[]
        self.objs:List[GameObject]=[]
        for i in range(self.num_hoists):
            obj=GameObject()
            h=obj.add_component(Hoist)
            h.code=f'H{i+1}'
            h.center=self.center
            if i==0:
                h.x=self.offsets[0]
            elif i==self.num_hoists-1:
                h.x=self.offsets[-1]
            else:
                h.x=self.offsets[0]+G.HOIST_SAFE_DISTANCE*i
            h.fsm.add_state(FreeState(h))
            h.fsm.add_state(MovingState(h))
            h.fsm.add_state(LoweringState(h))
            h.fsm.add_state(LiftingState(h))
            h.fsm.set_state('FreeState')
            self.objs.append(obj)
            self.hoists.append(h)
        obj=GameObject()
        t:Tank=obj.add_component(Tank)
        self.objs.append(obj)
        job=obj.add_component(Workpiece)
        t.job_in(job)

    def update(self,dt,t):
        if self.is_over:
            return
        for obj in self.objs:
            obj.update(dt,t)
        for h1 in self.hoists:
            for h2 in self.hoists:
                if h1==h2:
                    continue
                dis=round(abs(h1.x-h2.x))
                
                if (dis<G.HOIST_SAFE_DISTANCE):
                    print(h1,h2,dis)
                    if isinstance(h1.cmd,TransportCommand) and isinstance(h2.cmd,TransportCommand):
                        if h1.cmd.urgency>h2.cmd.urgency:
                            self.avoid(h2, h1)     
                        elif h2.cmd.urgency>h1.cmd.urgency:
                            self.avoid(h1, h2)     
                        else:
                            self.is_over=True
                            self.center.publish('on_hited',self)
                            return
                    elif isinstance(h1.cmd,TransportCommand):
                        if not self.avoid(h2, h1):
                            return                    
                    elif isinstance(h2.cmd,TransportCommand):
                       if not  self.avoid(h1, h2):
                           return
                    else:
                        self.avoid(h1, h2)  
                    

    def avoid(self, h1:Hoist, h2:Hoist):
        dx=h1.x-h2.x
        dx=dx/abs(dx+G.EPS)
        s=h1.fsm.current_state
        if isinstance(s,FreeState) or isinstance(s,MovingState):
            h1.x+=dx
            print(f'{h2}-->{h1}')
            return True
        print(f'{h1} buzy!')
        self.is_over=True
        return False
    
    def render(self,batch):
        if len(self.sprites)<=0:
            for h in self.hoists:
                self.sprites.append(BorderedRectangle(0,0,48,24,color=(0,255,0,100),batch=batch))
                #self.sprites.append(Circle(0,0,20,batch=batch))

        for i,sp in enumerate(self.sprites):
            h:Hoist=self.hoists[i]
            sp.x=(h.x+1)*64
            sp.y=(h.y+1)*64
                


