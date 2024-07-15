
from typing import List,Tuple
from pathlib import Path
from src.core import Task

from . import IParse



    # def to_list2(self):
    #     ms, ts = [], []
    #     for job, tasks in enumerate(self.data.jobs_data):
    #         t1, t2 = [], []
    #         for task in tasks:
    #             t1.append(task[0])
    #             t2.append(task[1])
    #         ms.append(t1)
    #         ts.append(t2)
    #     return ms, ts

    # def to_text(self, separator='\t'):
    #     """
    #         Convert matrix form of the data into test form
    #     :param separator: the separator char
    #     :return: the standard text form of the instance
    #     """
    #     op_per_mch = 1
    #     num_tasks_job = self.data.num_tasks
    #     op_pt = self.data.op_times
    #     n_j = len(num_tasks_job)
    #     _, n_m = op_pt.shape
    #     lines = [f'{n_j}{separator}{n_m}{separator}{op_per_mch}']
    #     op_idx = 0
    #     for j in range(n_j):
    #         line = f'{num_tasks_job[j]}'
    #         for _ in range(num_tasks_job[j]):
    #             indexs_machine = np.where(op_pt[op_idx] > 0)[
    #                 0]  # np.whaer 返回元组(indexs,)
    #             line = line + f'{separator}{len(indexs_machine)}'
    #             for k in indexs_machine:
    #                 line = line + \
    #                     f'{separator}{(k + 1)}{separator}{op_pt[op_idx][k]}'
    #             op_idx += 1
    #         lines.append(line)
    #     return '\n'.join(lines)
