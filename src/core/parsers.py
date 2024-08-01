from abc import ABC, abstractmethod
from typing import List,Dict
import numpy as np
from collections import defaultdict
import pandas as pd
from pathlib import Path
from . import Task,Instance
from ..datadef import G
from ..utils.split import *
__all__=['IParse','ExcelFileParser','StandardFjspFileParser','StandardJspFileParser' ]
# 定义一个接口类
class IParse(ABC):
    @abstractmethod
    def parse(self,fname:str)->Instance:
        pass

    def debug(self,info:Instance):
        for task in info.tasks:
            print(task.info)

class ExcelFileParser(IParse):
    def parse(self,fname:str)->Instance:
        fp=Path(__file__).parent.parent.parent/('data/'+ fname)
        name=fp.stem
        tasks:List[Task]=[]
        offsets:List[int]=[]
        df=pd.read_excel(fp,sheet_name="OpTime")
        machines=df.columns[1:].to_list()
        machine_names=[]
        agv_idxs=[]
        for i,machine_name in enumerate(machines):
            ss=machine_name.split('|')
            
            if len(ss)>=2:
                if len(ss)==3:
                    offsets.append([int(ss[1]),int(ss[2])])
                else:
                    offsets.append(int(ss[1]))
                machine_names.append(ss[0])
                if ss[0].startswith('AGV'):
                    agv_idxs.append(i)
            else:
                offsets.append(i)
        data=df.to_numpy()
        #print(data)
        task_idxs:Dict[int,int] =defaultdict(int)
        first_agv_idx=None if len(agv_idxs)==0 else min(agv_idxs)
        last_job_idx=0
        for row in data:
            job_idx=int(row[0])-1
            if last_job_idx!=job_idx:
                last_task=tasks[-1]
                last_job_idx=job_idx
                last_task.is_last=True
            task_idx=task_idxs[job_idx]
            task_idxs[job_idx]+=1
            ms=row[1:].copy()
            if first_agv_idx!=None:
                ms[first_agv_idx:]=0
            #idx=np.argmax(ms)
            task1=Task(job_idx,task_idx,ms,job_idx)
            tasks.append(task1)
            #print(task1)
            if first_agv_idx!=None:
                agvs=row[1:].copy()
                agvs[:first_agv_idx]=0
                if sum(agvs)>0:
                    task2=Task(job_idx,task_idx+1,agvs,job_idx)
                    task_idxs[job_idx]+=1
                    tasks.append(task2)
                    #print(task2)

        last_task=tasks[-1]
        last_task.is_last=True
        
        return Instance(name,tasks,offsets,machine_names,first_agv_idx)


class StandardFjspFileParser(IParse):
    def parse(self,fname:str)->Instance:
        fp=Path(__file__).parent.parent.parent/('data/'+ fname)
        name=fp.stem
        tasks:List[Task]=[]
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
                #max_runtime=0
                for k in range(num_machine):
                    mch_idx = data[idx + 2 * k + 1]-1
                    pt = data[idx + 2 * k + 2]  # 加工处理时间
                    times[mch_idx]=pt
                    # if max_runtime<pt:
                    #     max_runtime=pt
                task=Task(job_idx,task_idx,times,job_idx)
                tasks.append(task)
                idx = next_idx
        return Instance(name,tasks,list(range(n_m)),[],None)

class StandardJspFileParser(IParse):
    def parse(self,fname:str)->Instance:
        """
            Convert text form of the data into matrix form
        :param text: the standard text form of the instance
        """
        fp=Path(__file__).parent.parent.parent/('data/'+ fname)
        name=fp.stem
        tasks:List[Task]=[]
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
                task=Task(job_idx,i//2,op_times=times)
                tasks.append(task)
        return Instance(name,tasks,list(range(n_m)),[],None)