from  functools  import lru_cache
from pathlib import Path
import numpy as np
from typing import Dict,List
from dataclasses import dataclass
from collections import namedtuple,defaultdict
from sortedcontainers import SortedDict 
from jsplab.utils import TextHelper
from jsplab.conf import G
# OpConfig = namedtuple("OpConfig", "key name color")
#ProcStep= namedtuple("ProcStep", "tank_index offset min_time max_time")
#HoistPos= namedtuple("HoistPos", "tick x")
@dataclass
class HoistPos:
    tick:int
    x:int
    def __str__(self):
        return f"{self.tick}|{self.x}"
    def __repr__(self) -> str:
        return self.__str__()
@dataclass
class ProcStep:
    tank_index:int
    offset:int
    min_time:int
    max_time:int
    def __repr__(self) -> str:
        return self.__str__()
    def __str__(self):
        return f"T{self.tank_index+1}|{self.offset} {self.min_time}->{self.max_time}"
class MultiHoistProblem:
    def __init__(self,fpath='mhp/t4j2.csv',num_hoists=2):
        self.tank_offsets:List[int]=[]
        self.procs:List[List[ProcStep]]=[]
        self._num_hoists=num_hoists
        self.reset(fpath)
        
        
    def reset(self,fpath:str):
        for p in self.procs:
            p.clear()
        self.procs.clear()
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

    @staticmethod
    def get_left_hoists(start:int,x:float,num_hoists=2,safe_dis=1):
        assert start<=x
        dis=abs(start-round(x))
        k=dis//safe_dis
        rt= set(range(num_hoists))
        rt1 = set(range(k+1)) 
        return rt&rt1

    
    @staticmethod
    def get_right_hoists(start:int,x:float,num_hoists=2,safe_dis=1):
        assert start>=x
        dis=abs(start-round(x))
        k=dis//safe_dis
        rt= set(range(num_hoists))
        rt1 = set(range(num_hoists-1,num_hoists-1-k-1,-1)) 
        return rt&rt1
    
    def get_hoist_bound(self,hoist_index):
        n=self.num_hoists
        D=G.HOIST_SAFE_DISTANCE
        k=n-1-hoist_index
        x1=self.min_offset+hoist_index*D
        x2=self.max_offset-k*D
        assert x1<x2
        return (x1,x2)
    
    def select_hoists_by_offset(self,offset)->List[int]:
        n=self.num_hoists
        D=G.HOIST_SAFE_DISTANCE
        lhs=self.get_left_hoists(self.min_offset,offset,n,D)
        rhs=self.get_right_hoists(self.max_offset,offset,n,D)
        print(lhs,rhs)
        return list(lhs&rhs)
    
    def get_times_ticks(self,up_time=2,down_time=2,speed=1):
        rt=[]
        for proc_idx,proc in enumerate(self.procs):
            # print(f'P{proc_idx+1}')
            times=SortedDict() #key:移动i的起点
            t0=0
            for i in range(1,len(proc)):
                s1=proc[i-1]
                s2=proc[i]
                # print(s1,s2)
                op_time=s2.min_time
                dt=abs(s2.offset-s1.offset)//speed
                times[t0]=[HoistPos(0,s1.offset),HoistPos(up_time,s1.offset),
                           HoistPos(up_time+dt,s2.offset),HoistPos(up_time+dt+down_time,s2.offset)]
                # print(t0,times[t0])
                t0+=up_time+dt+down_time+op_time
            rt.append(times)

        return rt

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