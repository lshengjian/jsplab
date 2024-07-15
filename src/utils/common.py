import numpy as np
from typing import List,Tuple
from omegaconf import OmegaConf

from enum import Enum
class MoveType(Enum):
    stop='o'
    right='→'
    up='↑'
    left='←'
    down='↓'
    def __str__(self):
        return self.value

MOVE_FLAGS = [flag for _, flag in MoveType.__members__.items()]

def one_hot(index:int,size:int):
    rt=np.zeros((size,))
    rt[index]=1
    return rt#.tolist()

def load_config(fname:str):
    cfg = OmegaConf.load(fname)
    #print(**cfg)
    return cfg


def get_agv_flags(agv_pos:List[int],moves:List[Tuple[int,int]],down_time=2,up_time=2):
    size=len(agv_pos)
    rt:List[str]=[MoveType.stop]*size
    for t in range(size-1):
        cur_x=agv_pos[t]
        next_x=agv_pos[t+1]
        if next_x>cur_x:
            rt[t]=MoveType.right
        elif next_x<cur_x:
            rt[t]=MoveType.left
    for t1,t2 in moves:
        cur_x=agv_pos[t]
        for t in range(up_time):
            rt[t+t1]=MoveType.up
        for t in range(1,down_time+1):
            rt[t2-t]=MoveType.down
    return rt


if __name__ == '__main__':

    load_config('conf/demo/or-tools-solver.yaml')

