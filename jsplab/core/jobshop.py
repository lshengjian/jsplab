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
        self.center.subscribe('on_scheduling',self.on_scheduling)
        self.center.subscribe('on_timeout',self.on_timeout)
        

        self.reset()
    def on_scheduling(self,tank:Tank):
        print('on_scheduling',tank)
        tank.plan_hoist=self.hoists[0]
    def on_timeout(self,tank:Tank):
        print('on_timeout',tank)
        self.is_over=True
    def exe(self,hoist_id,cmd:Union[ShiftCommand,TransportCommand]):
        self.hoists[hoist_id].cmd=cmd

    def reset(self):
        self.is_over=False
        self.hoist_sprites=[]
        self.tank_sprites=[]
        self.hoists:List[Hoist]=[]
        self.tanks:List[Tank]=[]
        #self.objs:List[GameObject]=[]
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
            #self.objs.append(obj)
            self.hoists.append(h)
        obj=GameObject()
        t:Tank=obj.add_component(Tank)
        t.slot=1
        t.center=self.center
        #self.objs.append(obj)
        job=Job('A',0,[Task(1,12,999,[3,4]),Task()])
        t.put_job(job)
        self.tanks.append(t)

    def update(self,dt,t):
        if self.is_over:
            return
        for h in self.hoists:
            h.game_object.update(dt,t)
        for t in self.tanks:
            t.game_object.update(dt,t)
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
        if len(self.hoist_sprites)<=0:
            for h in self.hoists:
                self.hoist_sprites.append(BorderedRectangle(0,0,48,24,color=(0,255,0,100),batch=batch))
                #self.sprites.append(
        if len(self.tank_sprites)<=0:
            for t in self.tanks:
                self.tank_sprites.append(Circle(0,0,20,batch=batch))
        for i,sp in enumerate(self.hoist_sprites):
            h:Hoist=self.hoists[i]
            sp.x=(h.x+1)*64
            sp.y=(h.y+1)*64
                
        for i,sp in enumerate(self.tank_sprites):
            t:Tank=self.tanks[i]
            sp.x=(t.x+1)*64
            sp.y=64

