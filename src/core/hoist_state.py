from typing import List,Tuple
from .hoist import HoistFlag


def make_hoist_states(agv_pos:List[int],moves:List[Tuple[int,int]],down_time=2,up_time=2):
    size=len(agv_pos)
    rt:List[str]=[HoistFlag.stop]*size
    for t in range(size-1):
        cur_x=agv_pos[t]
        next_x=agv_pos[t+1]
        if next_x>cur_x:
            rt[t]=HoistFlag.right
        elif next_x<cur_x:
            rt[t]=HoistFlag.left
    for t1,t2 in moves:
        cur_x=agv_pos[t]
        for t in range(up_time):
            rt[t+t1]=HoistFlag.up
        for t in range(1,down_time+1):
            rt[t2-t]=HoistFlag.down
    return rt

def demo():
    #time   0   1   2   3   4   5   6   7   8   9   0   1   2   3   4
    pos   =[3,  2,  1,  0,  0,  0,  1,  2,  3,  4,  4,  4,  3,  3,  3]
    #step1 '←','←','←','o','o','→','→','→','→','o','o','←','o','o','o'
    #step2 '←','←','←','↑','↑','→','→','→','→','↓','↓','←','o','o','o'

    info=make_hoist_states(pos,[(3,11)])
    info=list(map(str,info))
    assert info==['←', '←', '←', '↑', '↑', '→', '→', '→', '→', '↓', '↓', '←', 'o', 'o', 'o']


if __name__ == '__main__':
    demo()
