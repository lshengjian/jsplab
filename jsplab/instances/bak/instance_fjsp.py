
import numpy as np
from typing import List,Tuple
from pathlib import Path
from jsplab.core import Task
from jsplab.utils.text_helper import text2nums, clean_comment
from . import IParse




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
    #                 0]  # np.where 返回元组(indexs,)
    #             line = line + f'{separator}{len(indexs_machine)}'
    #             for k in indexs_machine:
    #                 line = line + \
    #                     f'{separator}{(k + 1)}{separator}{op_pt[op_idx][k]}'
    #             op_idx += 1
    #         lines.append(line)
    #     return '\n'.join(lines)
