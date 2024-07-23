from __future__ import annotations

from dataclasses import dataclass as component
from typing import Tuple
import numpy as np
from enum import IntEnum

class NodeType(IntEnum): 
    Crane = 1 #Machine
    Tank = 2 #Machine
    Operate =4
    
class ProductAction(IntEnum): 
    Noop = 0
    Next = 1
    SelectCurrent = 2 
    

'''

top
o-------->  x
|
|
↓ y 
bottom
'''
class CraneAction(IntEnum): 
    Stay = 0
    Right = 1
    Top = 2 # to top
    Left = 3
    Bottom = 4
    
   
    
Directions = ["o","→","↑","←","↓"]
  
DIR_TO_VEC = [ 
    np.array((0, 0)),
    np.array((1, 0)),
    np.array((0, -1)),
    np.array((-1, 0)),
    np.array((0, 1)),
]
    
@component
class Color:
    r:int = 0
    g:int = 0
    b:int = 0
    a:int = 255
    @property
    def rgb(self):
        return self.r,self.g,self.b
    @property
    def rgba(self):
        return self.r,self.g,self.b,self.a
    def __str__(self) -> str:
        return f'{self.rgb}'
@component
class State:
    node_type:NodeType=0 
    op_key:int = 0
    product_code:str = ''
    x:float = 0.
    y:float = 0.
    #utilization_rate:float = 0.
    op_duration:int=0
    op_time:int=0

    def clone(self) -> State:
        return State(self.node_type, self.op_key, self.product_code, \
                     self.x, self.y, \
                     self.op_duration, self.op_time   )
@component
class Index:
    id:int =0
    def __eq__(self, other):
        return self.id == other.id
    def __hash__(self):
        return hash(self.id)

@component
class OperateData(Index):
    key:int=0
    name:str=''
    color:Color=Color()
    def __str__(self) -> str:
        return f'[{self.key}]{self.name} {self.color}'

@component
class TankData(Index):
    group:int=1
    op_key:int=0
    offsets:Tuple=tuple()
    
    op_name:str=''
    def __str__(self) -> str:
        xs='|'.join(map(str,self.offsets))
        return f'[{self.group}] {self.op_name} {xs}'
    
@component
class CraneData(Index):
   group:int=0
   name:str=''
   offset:int=0.0
   speed_x:float=1.0
   speed_y:float=1.0
   def __str__(self) -> str:
        return f'[{self.group}] {self.name} {self.offset} ({self.speed_x},{self.speed_x})'
   
@component
class OpTimeData(Index):
   product_code:str=''
   op_key:int=0
   wait_time:float=0.
   op_time:float=0.
   drop_time:float=0.
   
   op_name:str=''
#    @property
#    def duration(self):
#        return self.op_time
   def __str__(self) -> str:
        return f'[{self.product_code}] {self.op_name} {self.op_time}[{self.wait_time},{self.drop_time}]'