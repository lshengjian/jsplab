from __future__ import annotations
from typing import Tuple
from enum import Enum
import numpy as np
from .machine import Machine
from ..datadef import G,Event,PushAway


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

    def __init__(self,index=0,offset=0,name='',max_steps=30,min_offset=0,max_offset=0):
        super().__init__(index,offset,name)
        self._observers = []
        self.MAX_STEPS=max_steps
        if self.index==0:
            max_offset-=G.CRANE_SAFE_DISTANCE
        self.min_offset=min_offset
        self.max_offset=max_offset

        self.reset()
    
    @property
    def offset(self):
        return self.pos[self.last_time]
    
    @offset.setter 
    def offset(self,val):
        self.pos[self.last_time:]=val 

    def add_subscriber(self, observer):
        if observer not in self._observers and observer!=self:
            self._observers.append(observer)
    def debug(self):
        logger.debug(self,self.pos[:self.last_time])
    def remove_subscriber(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self,event:Event):
        event.sender=self
        event.time_step=self.last_time
        for observer in self._observers:
            #logger.debug(event)
            observer.update(event)

    def is_locked(self,time_step):
        for task in self.sort_tasks.values():
            if task.time_started<=time_step<=task.time_finished:
                return True
        return False
    def reset(self):
        super().reset()
        self._observers.clear()
        self.pos=np.array([self._offset]*(self.MAX_STEPS+1),dtype=int)
    
    def push_away(self,event:PushAway):
        agv:OverHeadCrane=event.sender
        x1=event.x1
        x2=event.x2
        dx=x2-x1
        dir=round(dx/abs(dx))
        p=self.offset

        for x in range(x1,x2+dir,dir):
            if abs(x-p)<G.CRANE_SAFE_DISTANCE :
                self.move_step(dir)
                
                p=self.offset
                logger.debug(f'{agv}|{x} push away:{self}|{p}')
                self.debug(self.last_time)


        


            

    def update(self,event:Event):
        if  isinstance(event,PushAway):
            self.push_away(event)

           
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
        if end<self.last_time:
            end=self.last_time
            pre_task_start=end-pre_task_runtime
        dx=x1-x0
        dir=0 if x1==x0 else dx/abs(dx)
        wait_times=end-self.last_time-abs(dx)
        if wait_times>0:
            for _ in range(wait_times):
               self.move_step(0)  #Wait for the processing to finish 
        if abs(dir)>0:
            #print(f'{self.name} notify:{x0}->{x1}')
            self.notify(PushAway(0,0,x0,x1))
        for _ in range(abs(dx)):
            self.move_step(dir) #Move to the processing tank that is about to end.

     
        t2=self.last_time
        for _ in range(G.CRANE_UP_TIME):
            self.move_step(0)
       
        dx=x2-x1
        dir=0 if x1==x2 else dx/abs(dx)
        if abs(dir)>0:
            #print(f'{self.name} notify:{x1}->{x2}')
            self.notify(PushAway(0,0,x1,x2))
        for _ in range(abs(dx)):
            self.move_step(dir)#Move to the next processing tank.
 
        for _ in range(G.CRANE_DOWN_TIME): 
            self.move_step(0)

        self.pos[self.last_time:]=self.pos[self.last_time]
        t3=self.last_time
        logger.debug(f'{self} move {x0}->{x1}:{t2-t1} {x1}->{x2}:{t3-t2}')
        return t2-t1,t3-t2

    def move_step(self, dir):
        x0=self.offset
        self.last_time+=1
        x1=x0+dir
        if x1<self.min_offset:
            x1=self.min_offset
        if x1>self.max_offset:
            x1=self.max_offset
        if (x0!=x1):
            self.offset=x1

  
            
