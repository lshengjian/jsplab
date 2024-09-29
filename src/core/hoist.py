from __future__ import annotations
from typing import Tuple
from enum import Enum
import numpy as np
from .machine import Machine
from ..datadef import G


import logging
logger = logging.getLogger(__name__.split('.')[-1])

class HoistFlag(Enum):
    stop='o'
    right='→'
    up='↑'
    left='←'
    down='↓'
    def __str__(self):
        return self.value

HoistFlags = [val for _, val in HoistFlag.__members__.items()]


class Hoist(Machine):
    def __init__(self,index,offsets,name,max_record_steps=100):
        
        super().__init__(index,offsets,name)
        self.max_record_steps=max_record_steps
        
        #self._observers = []
        self.reset()
    
    @property
    def offset(self):
        return self.history[self.last_time]
    
    @offset.setter 
    def offset(self,val):
        self.history[self.last_time:]=val 



    # def debug(self):
    #     logger.debug(self,self.history[:self.last_time])


    def is_locked(self,time_step):
        for task in self.sort_tasks.values():
            if task.time_started<=time_step<=task.time_finished:
                return True
        return False
    
    def reset(self):
        super().reset()
        self.history=np.array([self.offsets[0]]*(self.max_record_steps+1),dtype=int)
        
        #self._observers.clear()
        

           
    def debug(self):
        steps=self.max_record_steps
        print(f'{self.name}[{self.offset}]')
        for t in range(steps):
            print(f'{t:02d} ',end='')
        print()
        for t in range(steps):
            x=self.history[t]
            print(f'{x:2.0f} ',end='')
        print()

    def move_empty(self,x1:int,x2:int)->int:
        dx=x2-x1
        t1=self.last_time
        dir=0 if x1==x2 else dx/abs(dx)
        for _ in range(abs(dx)):
            self._move_step(dir)#Move to the next processing tank.
        t2=self.last_time
        return t2-t1

    def pickup_dropdown(self,x1:int,x2:int,pre_task_end:int)->Tuple[int]:
        end=pre_task_end
        if self.last_time>pre_task_end:
            logger.warning(f"pre task end time {pre_task_end}<{self.last_time}! ( {self})")
            end=self.last_time
 
        x0=self.offset
        t1=self.last_time
        
        t2 = self._move1( x0,x1, end)
       
        t3 = self._move2(x1, x2)
        self.history[self.last_time:]=self.history[self.last_time]
        
        logger.debug(f'{self} move {x0}->{x1}:{t2-t1} {x1}->{x2}:{t3-t2}')
        return t2-t1,t3-t2

    def _move2(self, x1, x2):
        dx=x2-x1
        dir=0 if x1==x2 else dx/abs(dx)
        for _ in range(abs(dx)):
            self._move_step(dir)#Move to the next processing tank.
 
        for _ in range(G.HOIST_DOWN_TIME): 
            self._move_step(0)
        t3=self.last_time
        return t3

    def _move1(self, x0,x1,  end):
        dx=x1-x0
        dir=0 if x1==x0 else dx/abs(dx)
        wait_times=end-self.last_time-abs(dx)/G.HOIST_VELOCITY[0]
        if wait_times>0:#等待前一加工任务完成
            for _ in range(int(wait_times)):
               self._move_step(0)  #Wait for the processing to finish 
        # if abs(dir)>0:
        #     #print(f'{self.name} notify:{x0}->{x1}')
        #     self.notify(PushAway(0,0,x0,x1))
        for _ in range(abs(dx)):
            self._move_step(dir) #Move to the processing tank that is about to end.

     
        t2=self.last_time
        for _ in range(G.HOIST_UP_TIME):
            self._move_step(0)
        return t2

    def _move_step(self, dir):
        x0=self.offset
        self.last_time+=int(1/G.HOIST_VELOCITY[0])
        x1=x0+dir
        if x1<self.offsets[0] or x1>self.offsets[1]:
            raise ValueError("out of offsets!")
        if (x0!=x1):
            self.offset=x1

  
            
    
    # def push_away(self,event:PushAway):
    #     agv:Hoist=event.sender
    #     x1=event.x1
    #     x2=event.x2
    #     dx=x2-x1
    #     dir=round(dx/abs(dx))
    #     p=self.offset

    #     for x in range(x1,x2+dir,dir):
    #         if abs(x-p)<G.HOIST_SAFE_DISTANCE :
    #             self.move_step(dir)
                
    #             p=self.offset
    #             logger.debug(f'{agv}|{x} push away:{self}|{p}')
    #             self.debug(self.last_time)

    # def add_subscriber(self, observer):
    #     if observer not in self._observers and observer!=self:
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
    #         observer.update(event)
    # def update(self,event:Event):
    #     if  isinstance(event,PushAway):
    #         self.push_away(event)
