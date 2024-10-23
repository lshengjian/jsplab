from  functools  import lru_cache
from pathlib import Path
import numpy as np
from typing import Dict,List
from collections import namedtuple,defaultdict
from jsplab.utils import TextHelper
# OpConfig = namedtuple("OpConfig", "key name color")
ProcStep= namedtuple("ProcStep", "tank_index offset min_time max_time")

class MultiHoistProblem:
    def __init__(self,fpath='mhp/h2j2.csv'):
        self.tank_offsets:List[int]=[]
        self.procs:List[List[ProcStep]]=[]
        data_root=Path(__file__).parent.parent.parent
        lines=TextHelper.get_data(data_root/f'data/{fpath}')
        for i,d in enumerate(lines[0]):
            self.tank_offsets.append(d)

        
        for i in range(1,len(lines),3):
            steps=[]
            ts=lines[i]
            opt1=lines[i+1]
            opt2=lines[i+2]
            for j in range(len(ts)):
                tank_index=ts[j]
                steps.append(ProcStep(tank_index,self.tank_offsets[tank_index],opt1[j],opt2[j]))
            self.procs.append(steps)
        





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