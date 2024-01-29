
import numpy as np

from typing import List
from .text_helper import text2nums, clean_comment
from ..instances import Instance
from .. import FJSP_Data


class InstanceFJSP(Instance):
    def parse(self, lines: List[str]):
        """
            Convert text form of the data into matrix form
        :param text: the standard text form of the instance
        """

        lines = clean_comment(lines)
        n_j, n_m = lines[0][0], lines[0][1]  # 作业数量，机器数量,机器平均任务数
        num_tasks_job = np.zeros(n_j, dtype='int32')  # 作业任务数量
        op_pt = []  # 加工处理时间

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
                op_pt.append(op_pt_row)

        op_pt = np.array(op_pt)
        self.data = FJSP_Data(self.name, num_tasks_job, op_pt)

    def to_text(self, separator='\t'):
        """
            Convert matrix form of the data into test form
        :param separator: the separator char
        :return: the standard text form of the instance
        """
        op_per_mch = 1
        num_tasks_job = self.data.num_tasks
        op_pt = self.data.op_times
        n_j = len(num_tasks_job)
        _, n_m = op_pt.shape
        lines = [f'{n_j}{separator}{n_m}{separator}{op_per_mch}']
        op_idx = 0
        for j in range(n_j):
            line = f'{num_tasks_job[j]}'
            for _ in range(num_tasks_job[j]):
                indexs_machine = np.where(op_pt[op_idx] > 0)[
                    0]  # np.where 返回元组(indexs,)
                line = line + f'{separator}{len(indexs_machine)}'
                for k in indexs_machine:
                    line = line + \
                        f'{separator}{(k + 1)}{separator}{op_pt[op_idx][k]}'
                op_idx += 1
            lines.append(line)
        return '\n'.join(lines)
