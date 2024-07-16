from collections import namedtuple
from typing import List
OpInfo = namedtuple("OpInfo", "start end job_idx task_idx")
class Machine:
    def __init__(self,index=0):
        self.index=index
        self.ops:List[OpInfo]=[] 
        self._last_time=0

    def add_op(self,start:int,duration:int,job_idx=-1 ,task_idx=-1)->int:
        end=start+duration
        last=0
        found=False
        
        for op in self.ops:
            if op.start-last>=duration and last<=start: #能插进空隙中去
                self.ops.append(OpInfo(start,end,job_idx,task_idx))
                found=True
                break
            last=op.end
        if not found:
            if self._last_time>start:
                end=self._last_time+duration
                self.ops.append(OpInfo(self._last_time,end,job_idx ,task_idx))
                self._last_time+=duration
            else:
                self.ops.append(OpInfo(start,end,job_idx ,task_idx))
                self._last_time=end
        self.ops.sort()
        return end
    
    @property 
    def last_time(self):  
        return self._last_time

    def utilization_rate(self,cur_time:int=0): 
        total=0
        for op in self.ops:
            if cur_time<op.end:
                cur_time=op.end
            total+=op.end-op.start
        return total/cur_time if cur_time>0 else 0
    
    def __str__(self):
        rt = f'M{self.index+1}[{self.utilization_rate():.2f}]:'
        for op in self.ops:
            name =''  if op.job_idx<0 and op.task_idx<0 else f'{op.job_idx+1}-{op.task_idx+1}'
            rt += f'{name} {op.start}->{op.end}|'
        return    rt 
if __name__ == "__main__":
    ma=Machine()
    #  [0,2]   [8,2]
    ma.add_op(0,2)
    assert ma.last_time==2
    ma.add_op(8,2)
    assert ma.last_time==10
    ma.add_op(2,3)
    #print(ma.ops)
    assert ma.last_time==10
    print(ma.utilization_rate(10))
    print(ma)
