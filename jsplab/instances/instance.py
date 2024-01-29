from typing import Dict,List
import pandas as pd
import numpy as np
from .text_helper import text2nums, clean_comment

from jsplab import OperateType
class Instance:
    def __init__(self, name):
        self.name = name
        self.job_size:Dict[str,int]={}
        self.nb_machine=0
        #self.op_times:NDArray=None
        self.data:List[List[List[OperateType]]]=[]

    def parse(self,fname:str):
        df=pd.read_excel(fname,sheet_name="OpTime",index_col =[0])
        op_times=df.to_numpy()
        task=df.index.to_list()
        job_size={}
        for op in task:
            job=op.split('-')[0]
            
            cnt=job_size.get(job,0)
            job_size[job]=cnt+1

        self.job_size=job_size

        cur=0
        self.nb_machine=op_times.shape[1]
        for cnt in self.job_size.values():
            ds=op_times[cur:cur+cnt]
            tasks=[]
            
            for d in ds:
                task=[]
                for i,t in enumerate(d):
                    if t>0:
                        task.append(OperateType(i,t))
                tasks.append(task)
            cur+=cnt
            self.data.append(tasks)


    def parse_text(self, lines: List[str]):
        """
            Convert text form of the data into matrix form
        :param text: the standard text form of the instance
        """

        lines = clean_comment(lines)
        n_j, n_m = lines[0][0], lines[0][1]  # 作业数量，机器数量,机器平均任务数
        num_tasks_job = np.zeros(n_j, dtype='int32')  # 作业任务数量
        op_times = []  # 加工处理时间

        for i in range(n_j):
            data = np.array(lines[i + 1])
            num_tasks_job[i] = data[0]

            idx = 1
            for j in range(data[0]):
                op_pt_row = np.zeros(n_m, dtype='int32')
                num_machine = data[idx]  # 该任务可在几台机器上进行
                next_idx = idx + 2 * num_machine + 1
                for k in range(num_machine):
                    mch_idx = data[idx + 2 * k + 1]
                    pt = data[idx + 2 * k + 2]  # 加工处理时间
                    op_pt_row[mch_idx - 1] = pt  # 实例中的机器编号从1开始编号的

                idx = next_idx
                op_times.append(op_pt_row)

        op_times = np.array(op_times)
        self.nb_machine=op_times.shape[1]
        for i,n in enumerate(num_tasks_job):
            self.job_size[str(i)]=n
        
        cur=0
        for cnt in self.job_size.values():
            ds=op_times[cur:cur+cnt]
            tasks=[]
            for d in ds:
                task=[]
                for i,t in enumerate(d):
                    if t>0:
                        task.append(OperateType(i,t))
                tasks.append(task)
            cur+=cnt
            self.data.append(tasks)




