from ..core import JobShop
import numpy as np
# def greedy_select(job:Job,ms:List[Machine]):
#     op_times=np.array(job.cur_task._runtimes)
#     op_times[op_times<1]=1e10
#     for i,t in enumerate(op_times):
#         op_times[i]=t*(1+ms[i].utilization_rate(job._last_time))
#     idxs=np.argsort(op_times)
#     job.assign(ms[idxs[0]])

def select_job(shop:JobShop,mask=[]):
    jobs=np.where(mask>0)[0]
    job_id=np.random.choice(jobs,1)[0]
    return job_id