from __future__ import annotations
from typing import Tuple
from enum import Enum
import numpy as np
from .machine import Machine
from ..datadef import G


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

    def __init__(self,index=0,offset=0,name='',max_steps=30):
        super().__init__(index,offset,name)
        #self._observers = []
        self.MAX_STEPS=max_steps
        self.reset()
    
    @property
    def offset(self):
        return self.pos[self.last_time]
    
    @offset.setter 
    def offset(self,val):
        self.pos[self.last_time:]=val 

    # def add_subscriber(self, observer):
    #     if observer not in self._observers:
    #         self._observers.append(observer)

    # def remove_subscriber(self, observer):
    #     try:
    #         self._observers.remove(observer)
    #     except ValueError:
    #         pass

    # def notify(self,event:Event):
    #     event.sender=self
    #     event.time_step=self.last_time
    #     for observer in self._observers:
    #         #logger.debug(event)
    #         observer.update(event)


    def reset(self):
        super().reset()
        #self._observers.clear()
        self.pos=np.array([self._offset]*(self.MAX_STEPS),dtype=int)
    
    # def push_away(self,event:PushAway):
    #     agv:OverHeadCrane=event.sender
    #     steps=abs(agv.offset-self.offset)
    #     if steps<G.CRANE_SAFE_DISTANCE:
    #         for _ in range(G.CRANE_SAFE_DISTANCE-steps):
    #             x=self.offset
    #             self.last_time+=1
    #             self.offset=x+event.dir
    #         logger.debug(event)
            

    # def update(self,event:Event):
    #     if  isinstance(event,PushAway):
    #         self.push_away(event)

           
    def debug(self,steps:int):
        print(f'{self.name}[{self._offset}]')
        for t in range(steps):
            print(f'{t:02d} ',end='')
        print()
        for t in range(steps):
            x=self.pos[t]
            print(f'{x:2.0f} ',end='')
        print()

    
    def move(self,x1:int,x2:int,pre_task_start:int,pre_task_runtime:int)->Tuple[int]:
        if self.last_time>pre_task_start:
            logger.warning(f"{self} update start time {pre_task_start}->{self.last_time}!")
            pre_task_start=self.last_time
        x0=self.offset
        t1=self.last_time
        end=pre_task_start+pre_task_runtime
        dx=x1-x0
        dir=0 if x1==x0 else dx/abs(dx)
        for _ in range(abs(dx)):
            self.move_step(dir) #Move to the processing tank that is about to end.
        if end<self.last_time:
            end=self.last_time
            pre_task_start=end-pre_task_runtime
        if end>self.last_time:
            for _ in range(end-self.last_time):
               self.move_step(0)  #Wait for the processing to finish      
        t2=self.last_time
        for _ in range(G.CRANE_UP_TIME):
            self.move_step(0)
       
        dx=x2-x1
        dir=0 if x1==x2 else dx/abs(dx)
        for _ in range(abs(dx)):
            self.move_step(dir)#Move to the next processing tank.
 
        for _ in range(G.CRANE_DOWN_TIME): 
            self.move_step(0)

        self.pos[self.last_time:]=self.pos[self.last_time]
        t3=self.last_time
        logger.debug(f'{self}|{t3} move {x0}->{x1}:{t2-t1} {x1}->{x2}:{t3-t2}')
        return t2-t1,t3-t2

    def move_step(self, dir):
        x=self.offset
        self.last_time+=1
        self.offset=x+dir
        if (x!=self.offset):
            self.pos[self.last_time:]=self.pos[self.last_time]
        #   self.notify(PushAway(0,0,self.offset,dir))
            
