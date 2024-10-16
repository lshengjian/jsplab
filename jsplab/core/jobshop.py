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

    def exe(self,hoist_id,cmd:Union[ShiftCommand,WorkCommand]):
        self.hoists[hoist_id].cmd=cmd

    def reset(self):
        self.sprites=[]
        self.hoists:List[Hoist]=[]
        self.objs:List[GameObject]=[]
        for i in range(self.num_hoists):
            obj=GameObject()
            h=obj.add_component(Hoist)
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

    def update(self,dt,t):
        for obj in self.objs:
            obj.update(dt,t)
        for h1 in self.hoists:
            for h2 in self.hoists:
                if h1==h2:
                    continue
                if (abs(h1.x-h2.x)<G.HOIST_SAFE_DISTANCE):
                    self.center.publish('on_hited',self)

    
    def render(self,batch):
        if len(self.sprites)<=0:
            for h in self.hoists:
                self.sprites.append(BorderedRectangle(0,0,48,24,color=(0,255,0,100),batch=batch))
                #self.sprites.append(Circle(0,0,20,batch=batch))

        for i,sp in enumerate(self.sprites):
            h:Hoist=self.hoists[i]
            sp.x=(h.x+1)*64
            sp.y=(h.y+1)*64
                


