
from __future__ import annotations
from typing import  List
from .crane import OverHeadCrane

# from collections import defaultdict
# from ..datadef.constant import Constant
# from src.utils import get_dataclass_by_name
# from omegaconf import OmegaConf
# import logging
# logger = logging.getLogger(__name__.split('.')[-1])


class JobShop:
    def __init__(self,cranes:List[OverHeadCrane],safe_distance=2):
        # config = OmegaConf.load("conf/constant.yaml")
        # self.args:Constant = get_dataclass_by_name('Constant')(**config)
        
        self.cranes:List[OverHeadCrane] =cranes  
        self.safe_distance=safe_distance 



    def is_safe(self,max_time:int)->bool:
        num_agvs=len(self.cranes)
        for t in range(max_time+1):
            for i in range(num_agvs-1):
                j=i+1
                dis=self.safe_distance
                if abs(self.cranes[i].pos[t]-self.cranes[j].pos[t]) < dis:
                    return False
                    #raise ValueError(f'{cache[i]} hit {cache[j]}')
        return True

    def reset(self):
        for agv in self.cranes:
            agv.reset()










 

 