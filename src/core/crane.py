from __future__ import annotations
from typing import Dict
from enum import Enum
import numpy as np
class CraneState(Enum):
    stop='o'
    right='→'
    up='↑'
    left='←'
    down='↓'
    def __str__(self):
        return self.value

CraneStringStates = [val for _, val in CraneState.__members__.items()]


class OverHeadCrane:
    MAX_STEPS=1000
    #SAFE_DISTANCE=2
    def __init__(self,index=0,offset=0,name='',up_time:int=2,down_time:int=2):
        self.index=index
        self.init_offset=offset
        self.UP_TIME=up_time
        self.DOWN_TIME=down_time
        self.name=name if len(name)>0 else f'H{index+1}'
        self.reset()
    
    def __str__(self) -> str:
        return f"{self.name}|{self.pos[self._last_time]}"
    
    def reset(self):
        self._last_time=0 
        self.pos=np.array([self.init_offset]*OverHeadCrane.MAX_STEPS,dtype=int)


    @property
    def offset(self):
        return self.pos[self._last_time]
    
    def debug(self):
        print(f'{self.name}[{self.offset0}]')
        for t in range(OverHeadCrane.MAX_STEPS):
            print(f'{t:02d} ',end='')
        print()
        for x in self.pos:
            print(f'{x:2.0f} ',end='')
        print()

    
    def move(self,start_time:int,from_offset:int,to_offset:int)->int:
        x0=self.pos[self._last_time]
        dx=from_offset-x0
        dir=0 if from_offset==x0 else dx/abs(dx)
        t1=self._last_time
        for _ in range(abs(dx)):
            self._last_time+=1
            self.pos[self._last_time]=self.pos[self._last_time-1]+dir
        if self._last_time>start_time:
            raise ValueError(f"{self} can't move at time={start_time}")
        for _ in range(start_time-self._last_time+self.UP_TIME): #UP_TIME=2
            self._last_time+=1
            self.pos[self._last_time]=self.pos[self._last_time-1]
        
        
        dx=to_offset-from_offset
        dir=0 if from_offset==to_offset else dx/abs(dx)
        for _ in range(abs(dx)):
            self._last_time+=1
            self.pos[self._last_time]=self.pos[self._last_time-1]+dir
        for _ in range(self.DOWN_TIME): 
            self._last_time+=1
            self.pos[self._last_time]=self.pos[self._last_time-1]
        self.pos[self._last_time:]=self.pos[self._last_time]
        return self._last_time-t1
