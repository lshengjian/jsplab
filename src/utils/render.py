from src.utils import console
from rich.text import Text
from typing import  List,Dict,Tuple
from collections import defaultdict
from src.agents.solver.util import assigned_task_type
import time

def print_info(info):
    console.print('',end='\r')
    for s in info:
        console.print(s,end='')

# def get_crane_states(steps:int,agv_start:int,cranes_pos,data:List[assigned_task_type])->Dict[int,List[int]]:
#     rt=defaultdict(list)
#     for i in range(len(cranes_pos)):
#         agv_idx=i+agv_start
#         ds:List[assigned_task_type]=data[agv_idx]
#         ts=[(d.start,d.start+d.duration) for  d in ds]
#         rt[i]=get_crane_states(cranes_pos[i],ts)
#     return rt

def replay(x1:int,x2:int,agv_start,steps:int,pause_time:int,offsets,data):
    #flags=get_crane_states(steps,agv_start,cranes_pos,data)
    
    info=[Text(f'{i:^4d}', style="bold yellow") for i in range(x1,x2+1)]
    print_info(info)
    console.print()
    for t in range(steps):
        info=[' '*4]*(x2-x1+1)
        #assert len(info)==self.max_x-self.min_x+1
        
        for k,x in enumerate(offsets):
            if k>=agv_start:
                continue
            m=f'M{k+1}'
            s=Text(f'{m:4s}', style="bold green")
            info[x]=s
        #console.print(f'\r{info}',end='')

        for i,agv in enumerate(data):
            x=agv[0][t]
            dir=agv[1][t]
            m=f'{i+1}{dir}'
            info[x]=s=Text(f'{m:4s}', style="red")
        print_info(info)
        time.sleep(pause_time) 

