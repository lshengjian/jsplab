from __future__ import annotations
from typing import Dict,Tuple
from enum import Enum
import numpy as np
from .machine import Machine
from ..datadef import *
from collections import namedtuple
from sortedcontainers import SortedDict



import logging
logger = logging.getLogger(__name__.split('.')[-1])

class CraneState(Enum):
    stop='o'
    right='→'
    up='↑'
    left='←'
    down='↓'
    def __str__(self):
        return self.value

CraneStringStates = [val for _, val in CraneState.__members__.items()]


class OverHeadCrane(Machine):

    def __init__(self,index=0,offset=0,name='',max_steps=30,up_time=None,down_time=None):
        super().__init__(index,offset,name)
        self.MAX_STEPS=max_steps
        self.UP_TIME=round(G.CRANE_HEIGHT/G.CRANE_VELOCITY[1]) if up_time is None else up_time
        self.DOWN_TIME=self.UP_TIME if down_time is None else down_time
        self.reset()
    
    @property
    def offset(self):
        return self.pos[self.last_time]
    
    @offset.setter 
    def offset(self,val):
        self.pos[self.last_time:]=val 

    def reset(self):
        self.last_time=0 
        self.avoids:Dict[int,AvoidCommand]=SortedDict()
        self.pos=np.array([self._offset]*self.MAX_STEPS,dtype=int)
    
    def push_away(self,event:PushAway):
        agv:OverHeadCrane=event.sender
        steps=abs(agv.offset-self.offset)
        #x=agv.offset
        #self.avoids[event.time_step]=AvoidCommand(event.pos,event.dir)
        if steps<G.CRANE_SAFE_DISTANCE:
            for _ in range(G.CRANE_SAFE_DISTANCE-steps):
                x=self.offset
                self.last_time+=1
                self.offset=x+event.dir
            logger.debug(event)
            




    def update(self,event:Event):
        if  isinstance(event,PushAway):
            self.push_away(event)

    


           
    def debug(self):
        print(f'{self.name}[{self._offset}]')
        for t in range(self.MAX_STEPS):
            print(f'{t:02d} ',end='')
        print()
        for x in self.pos:
            print(f'{x:2.0f} ',end='')
        print()

    
    def move(self,x1:int,x2:int,start_time:int=None)->Tuple[int,int]:
        if start_time is None:
            start_time=self.last_time
        start_time=min(start_time,self.last_time)
        x0=self.offset
        dx=x1-x0
        dir=0 if x1==x0 else dx/abs(dx)
        t1=self.last_time
        for _ in range(abs(dx)):
            self.move_step(dir)
        t2=self.last_time
            
        if self.last_time>start_time:
            logger.warning(f"{self} start time {start_time}->{self.last_time}!")
            start_time=self.last_time
            #raise ValueError(f"{self} can't move at time={start_time}")
        for _ in range(start_time-self.last_time+self.UP_TIME): #UP_TIME=2
            self.move_step(0)
       
        dx=x2-x1
        dir=0 if x1==x2 else dx/abs(dx)
        for _ in range(abs(dx)):
            self.move_step(dir)
        #self.notify(PushAway(0,0,self.offset+dir*G.CRANE_SAFE_DISTANCE,dir))
 
        for _ in range(self.DOWN_TIME): 
            self.move_step(0)

        self.pos[self.last_time:]=self.pos[self.last_time]
        t3=self.last_time
        logger.debug(f'{self} move {x0}->{x1}->{x2} time:{t3-t1}')
        return t3-t1,t2

    def move_step(self, dir):
        x=self.offset
        self.last_time+=1
        self.offset=x+dir
        if (x!=self.offset):
            self.notify(PushAway(0,0,self.offset,dir))
            
