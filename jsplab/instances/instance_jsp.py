
import numpy as np

from typing import List
from .text_helper import text2nums, clean_comment
from ..instances import Instance
from .. import JSP_Data, OperateType


class InstanceJSP(Instance):
    def parse(self, lines: List[str]):
        """
            Convert text form of the data into matrix form
        :param text: the standard text form of the instance
        """

        lines = clean_comment(lines)
        n_j, n_m = lines[0][0], lines[0][1]  # 作业数量，机器数量
        jobs = []

        for i in range(n_j):
            data = np.array(lines[i + 1])
            assert len(data) % 2 == 0
            job = []

            for j in range(0, len(data), 2):
                m, t = data[j], data[j+1]
                job.append(OperateType(m, t))
            jobs.append(job)
        self.data = JSP_Data(self.name, jobs)

    def to_list2(self):
        ms, ts = [], []
        for job, tasks in enumerate(self.data.jobs_data):
            t1, t2 = [], []
            for task in tasks:
                t1.append(task[0])
                t2.append(task[1])
            ms.append(t1)
            ts.append(t2)
        return ms, ts

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
                    0]  # np.whaer 返回元组(indexs,)
                line = line + f'{separator}{len(indexs_machine)}'
                for k in indexs_machine:
                    line = line + \
                        f'{separator}{(k + 1)}{separator}{op_pt[op_idx][k]}'
                op_idx += 1
            lines.append(line)
        return '\n'.join(lines)
