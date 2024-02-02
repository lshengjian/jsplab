from abc import ABC, abstractmethod
from typing import Tuple,List,Dict
#from dataclasses import dataclass as component
import pandas as pd
from pathlib import Path
from jsplab.core import Task
from jsplab.utils.text_helper import  clean_comment
import numpy as np
from collections import defaultdict,namedtuple

__all__=['InstanceInfo','IParse','ParserExcel','ParserStandardJspFile','ParserFjspFile']

DATA_DIR='data/instances/'
# InstanceInfo = namedtuple("InstanceInfo", \
#                           "name jobs machine_offsets first_agv_index")
# @component
# class InstanceInfo:
#     name:str=''
#     jobs:List[Task]=[]
#     machine_offsets:List[int]=[]
#     first_agv_index:int=0

#     def __str__(self) -> str:
#         return f'{self.name}[{self.first_agv_index}]'

class InstanceInfo:
    def __init__(self,name='',jobs:List[Task]=[], \
                 offsets:List[int]=[],first_agv_index:int=None):
        self.name:str=name
        self.jobs:List[Task]=jobs
        self.machine_offsets:List[int]=offsets
        self.first_agv_index:int=first_agv_index
        

    def __str__(self) -> str:
        return f'{self.name}|{self.machine_offsets}|{self.first_agv_index}'

# 定义一个接口类
class IParse(ABC):
    @abstractmethod
    def parse(self,fname:str)->InstanceInfo:
        pass

    def debug(self,info:InstanceInfo):
        for task in info.jobs:
            print(task.str_info())

class ParserExcel(IParse):
    def parse(self,fname:str)->InstanceInfo:
        fp=Path(DATA_DIR+fname)
        name=fp.stem
        jobs:List[Task]=[]
        offsets:List[Task]=[]
        df=pd.read_excel(fp,sheet_name="JobTime")
        machines=df.columns[1:].to_list()
        agv_idxs=[]
        for i,machine_name in enumerate(machines):
            ss=machine_name.split('|')
            if len(ss)==2:
                offsets.append(int(ss[1]))
                if ss[0].startswith('AGV'):
                    agv_idxs.append(i)
            else:
                offsets.append(i)
        data=df.to_numpy()
        task_idxs:Dict[int,int] =defaultdict(int)
        for row in data:
            job_idx=int(row[0])-1
            task_idx=task_idxs[job_idx]
            task_idxs[job_idx]+=1
            ms=row[1:] 
            task=Task(job_idx,task_idx,machine_times=ms)
            jobs.append(task)
        first_agv_idx=None if len(agv_idxs)==0 else min(agv_idxs)
        return InstanceInfo(name,jobs,offsets,first_agv_idx)

class ParserStandardJspFile(IParse):
    def parse(self,fname:str)->InstanceInfo:
        """
            Convert text form of the data into matrix form
        :param text: the standard text form of the instance
        """
        fp=Path(DATA_DIR+fname)
        name=fp.stem
        jobs:List[Task]=[]
        with open(fp, 'r') as f:
            lines = f.readlines()
        lines = clean_comment(lines)
        n_j, n_m = lines[0][0], lines[0][1]  # 作业数量，机器数量
        for job_idx in range(n_j):
            data = np.array(lines[job_idx + 1])
            assert len(data) % 2 == 0
            for i in range(0, len(data), 2):
                m, t = data[i], data[i+1]
                times=[0]*n_m
                times[m]=t
                task=Task(job_idx,i//2,machine_times=times)
                jobs.append(task)
        return InstanceInfo(name,jobs,list(range(n_m)),None)

class ParserFjspFile(IParse):
    def parse(self,fname:str)->InstanceInfo:
        fp=Path(DATA_DIR+fname)
        name=fp.stem
        jobs:List[Task]=[]
        with open(fp, 'r') as f:
            lines = f.readlines()
        lines = clean_comment(lines)
        n_j, n_m = lines[0][0], lines[0][1]  # 作业数量，机器数量,机器平均任务数
        for job_idx in range(n_j):
            data = np.array(lines[job_idx + 1])
            idx = 1
            for task_idx in range(data[0]): 
                times=[0]*n_m
                num_machine = data[idx]  # 该任务可在几台机器上进行
                next_idx = idx + 2 * num_machine + 1
                for k in range(num_machine):
                    mch_idx = data[idx + 2 * k + 1]-1
                    pt = data[idx + 2 * k + 2]  # 加工处理时间
                    times[mch_idx]=pt
                task=Task(job_idx,task_idx,machine_times=times)
                jobs.append(task)
                idx = next_idx
        return InstanceInfo(name,jobs,list(range(n_m)),None)

