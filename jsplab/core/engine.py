from sortedcontainers import SortedDict  
from typing import List
from collections import namedtuple

import logging,math
logger = logging.getLogger(__name__.split('.')[-1])


#HoistCfg = namedtuple("HoistCfg", "offset a1 a2 speed code group min_offset max_offset down_time up_time")
class Engine:
    def __init__(self,offset=0,a1=1,a2=1,speed=1):
        
        self.offset = offset
        self.a1 = a1 # 加速度
        self.a2 = a2 # 减速度
        self.V = speed# 稳定速度
        assert self.a1>0 and self.a2>0 and self.V>0
        # 计算加速和减速阶段的时间
        T1 = self.V / self.a1
        T2 = self.V / self.a2
        D1=0.5*self.V*T1
        D2=0.5*self.V*T2
        self.D=D1+D2 #临近距离
        self.T1=T1
        self.T2=T2
    def __str__(self):
        return f"{self.offset} D:{self.D} V:{self.V} T1:{self.T1} T2:{self.T2}"
    def plan(self,to_offset:float,t:float):
        target_dis:float=abs(to_offset-self.offset)
        dis=0
        if target_dis>=self.D:
            t2=(target_dis-self.D)/self.V #匀速运动时间
            if t<=self.T1:
                dis= 0.5*self.a1*t**2
            elif t<=self.T1+t2:
                dis= 0.5*self.a1*self.T1**2+(t-self.T1)*self.V
            else:
                if t>self.T1+self.T2+t2:
                    t=self.T1+self.T2+t2
                dis= target_dis-0.5*self.a2*(self.T1+self.T2+t2-t)**2
        else:
            t1 = math.sqrt(2 * target_dis/ (self.a1+self.a1**2/self.a2))
            t2=self.a1*t1/self.a2
            if t<=t1:
                dis= 0.5*self.a1*t**2
            else:
               if t>t1+t2:
                    t=t1+t2
               dis= target_dis-0.5*self.a2*(t1+t2-t)**2 
        dir=1 if to_offset>self.offset else -1
        pos=self.offset+dis*dir
        return pos

    def ETA(self,to_offset:float):#Estimated time of arrival
        target_dis:float=abs(to_offset-self.offset)
        if target_dis>=self.D:
            t2=(target_dis-self.D)/self.V #匀速运动时间
            return self.T1+self.T2+t2
        # v=t1.a1=t2.a2 ==> t2=t1*a1/a2
        # target_dis=0.5*a1*t1^2+0.5*t1^2*a2*a1^2/a2^2=0.5*t1^2*(a1+a1^2/a2)
        #  ==> t1=sqrt(2*target_dis/(a1+a1^2/a2))
        t1 = math.sqrt(2 * target_dis/ (self.a1+self.a1**2/self.a2))
        t2=self.a1*t1/self.a2
        return t1+t2



