from typing import List,Any
from dataclasses import dataclass

@dataclass 
class AvoidCommand:
    offset:int
    dir:int##dir>0 x>offset ;dir<0 x<offset
     
    def __str__(self):
        return f'{self.offset}[{self.dir}]'


@dataclass 
class Event:
    sender:Any
    time_step:int

    def __str__(self):
        return f'[{self.time_step}]{self.sender} fire {self.__class__.__name__} | {self.data}'
    @property
    def data(self):
        return ''
    
@dataclass 
class PushAway(Event):
    pos: int
    dir: int
    @property
    def data(self):
        return f'{self.pos}({self.dir})'

@dataclass 
class TaskDelayed(Event):
    plan_time: int
    finished_time: int
    @property
    def data(self):
        return f'{self.plan_time}->{self.finished_time}'