from  functools  import lru_cache
from pathlib import Path
import numpy as np
from typing import Dict,List
from collections import namedtuple,defaultdict
from jsplab.utils import TextHelper
# OpConfig = namedtuple("OpConfig", "key name color")
ProcStep= namedtuple("ProcStep", "tank_index offset min_time max_time")

class MultiHoistProblem:
    def __init__(self,fpath='mhp/t4j2.csv'):
        self.tank_offsets:List[int]=[]
        self._num_hoists=1
        self.procs:List[List[ProcStep]]=[]
        data_root=Path(__file__).parent.parent.parent
        lines=TextHelper.get_data(data_root/f'data/{fpath}')
        for i,d in enumerate(lines[0]):
            self.tank_offsets.append(d)
        
        self.min_offset=min(self.tank_offsets)
        self.max_offset=max(self.tank_offsets)
       
        for i in range(1,len(lines),3):
            steps=[]
            ts=lines[i]
            opt1=lines[i+1]
            opt2=lines[i+2]
            for j in range(len(ts)):
                tank_index=ts[j]
                steps.append(ProcStep(tank_index,self.tank_offsets[tank_index],opt1[j],opt2[j]))
            self.procs.append(steps)
        

    @property 
    def num_hoists(self)->int:
        return self._num_hoists
    
    @num_hoists.setter
    def num_hoists(self,m=2):
        self._num_hoists=m


    def get_times_ticks(self,up_time=2,down_time=2,speed=1):
        ticks=defaultdict(list) #移动i的相对时间，位置
        times=defaultdict(list) #移动i的时间起点
        for job_idx,proc in enumerate(self.procs):
            print(job_idx+1)
            for i in range(1,len(proc)):
                
                s1=proc[i-1]
                s2=proc[i]
                print(s2)
                op_time=0 if i==1 else s1.min_time
                dt=abs(s2.offset-s1.offset)//speed
                ticks[job_idx].append([(0,s1.offset),(up_time,s1.offset),(up_time+dt,s2.offset),(up_time+dt+down_time,s2.offset)])
                if i==1:
                    times[job_idx].append(0)
                else:
                    t0=times[job_idx][-1]
                    mt0=ticks[job_idx][-1][-1][0]
                    times[job_idx].append(t0+mt0+op_time)
                    
                    print(t0,mt0,op_time)
        return times,ticks

# def get_tanks(shop:str,opkey:Dict[str,int])->Dict[int,TankConfig]:
#     fpath=Path(__file__).parent.parent.parent/f'conf/{shop}/tanks.csv'
#     data = np.genfromtxt(fpath, delimiter=',', skip_header=1,dtype=str,encoding='utf-8')  
#     rt={}
#     for row in data:
#         op_name,slots=row
#         #cfg:OpConfig=op_dict[op_key]
#         ps=tuple(map(int,slots.split('~')))
#         if len(ps)==2:
#             for p in range(ps[0],ps[-1]+1):
#                 rt[p]=TankConfig(opkey[op_name],p) 
#         else:
#             ps=tuple(map(int,slots.split('|')))
#             if len(ps)>1:
#                 for p in ps:
#                     rt[p]=TankConfig(opkey[op_name],p)
#             else:
#                 rt[ps[0]]=TankConfig(opkey[op_name],ps[0])
#     return rt
        
# @lru_cache(1024)
# def get_offset(slot:int,shop:str=None):
#     '''
#     获取该槽位号距离轨道起点的总长度
#     '''
#     if shop is None:
#         return 1.0*slot
#     fpath=Path(__file__).parent.parent.parent/f'conf/{shop}/offsets.csv'
#     data = np.genfromtxt(fpath, delimiter=',', skip_header=1,encoding='utf-8')  
#     for item in data:
#         if slot==round(item[0]):
#             return float(item[1])
        
# def get_operates()->Dict[int,OpConfig]:
#     fpath=Path(__file__).parent.parent.parent/f'conf/operates.csv'
#     data = np.genfromtxt(fpath, delimiter=',', skip_header=1,dtype=str, encoding='utf-8') 
#     rt={}
#     for row in data:
#         key,name,color=row
#         c:str=color
#         cs=tuple(map(int,c.split('|')))
#         cfg=OpConfig(int(key),str(name),cs) 
#         rt[cfg.key]=cfg
#     return rt

# def get_opkey_dict(op_dict:Dict[int,OpConfig])->Dict[str,int]:
#     rt={}
#     for cfg in op_dict.values():
#         rt[cfg.name]=cfg.key
#     return rt