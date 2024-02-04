import numpy as np
from typing import List,Tuple
from jsplab.core import MOVE_FLAGS,MoveType
def one_hot(index:int,size:int):
    rt=np.zeros((size,))
    rt[index]=1
    return rt#.tolist()

def update_agv_history(agv_pos:List[int],moves:List[Tuple[int,int]],down_time=2,up_time=2):
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



