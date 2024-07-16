from ortools.sat.python import cp_model
from rich.text import Text
from .util import *
from ...utils import *
from src.utils.crane_state import get_crane_states
from src.core import convert2fjsp_data,Instance
from typing import  List,Dict,Tuple
import time
import numpy as np
def get_horizon(instance: Instance,agv_up_time=2,agv_down_time=2):
    rt=0
    for task_id in range(len(instance.tasks)-1):
        if task_id%2==0:
            task=instance.tasks[task_id]
            rt+=task.runtime
            #print(task_id+1,task.runtime)
        else:
            pre=instance.tasks[task_id-1]
            next=instance.tasks[task_id+1]
            #print(pre.str_info(),next.str_info())
            m1_idxs=pre.eligible_machines#np.nonzero(pre.machines)[0]
            m2_idxs=next.eligible_machines#np.nonzero(next.machines)[0]
            #print(pre.machines,m1_idxs)

            x1=instance.machine_offsets[m1_idxs[0]]#上个电镀作业的第一个机器位置
            x2=instance.machine_offsets[m2_idxs[-1]]#下个电镀作业的最后一个机器位置
            dt=abs(x2-x1)+agv_up_time+agv_down_time# todo
            #print(x1,x2,dt)
            rt+=dt 
    task=instance.tasks[-1]#最后一个加工处理
    rt+=task.runtime
    return rt
        

class OrToolSolver:
    def __init__(self,info: Instance,agv_up_time=2,agv_down_time=2):
        #self.info: InstanceInfo=info
        self.agv_up_time=agv_up_time
        self.agv_down_time=agv_down_time
        self.offsets = info.machine_offsets
        self.min_x, self.max_x = min(self.offsets), max(self.offsets)
        self.machines_count = len(self.offsets)
        self.jobs = convert2fjsp_data(info.tasks)
        self.agv_start = info.first_crane_index
        self.agv_num = self.machines_count - self.agv_start
        self.horizon=get_horizon(info,agv_up_time,agv_down_time)
        #self.horizon = sum(task.runtime if i%2==0 else 0 for i,task in enumerate(info.jobs))
        #self.horizon+=(self.max_x-self.min_x+agv_up_time+agv_down_time)*(len(info.jobs)//2)
        print(f"Max Time Steps:{self.horizon}")
        self.model = cp_model.CpModel()
        
        
    def init_agvs_pos(self):
        model=self.model
        agv_steps: List[cp_model.IntVar] = [None]*self.agv_num*self.horizon #把多维数组压缩为一维数组
        for agv in range(self.agv_num):
            agv_steps[agv*self.horizon]=model.NewConstant(self.offsets[self.agv_start + agv])
            for t in range(1, self.horizon):
                idx=agv*self.horizon+t
                agv_steps[idx]=model.NewIntVar(self.min_x, self.max_x, f'agv{agv}_{idx}')
                tp = model.NewIntVar(0, 1,'')
                p2 = agv_steps[idx]
                p1 = agv_steps[idx - 1]
                model.AddAbsEquality(tp, p2 - p1)  # 确保天车一个时间单位最多只移动一个位置

        # 确保天车顺序及安全距离
        for agv in range(self.agv_num - 1):
            for t in range(self.horizon):
                idx1=agv*self.horizon+t
                idx2=(agv+1)*self.horizon+t
                model.Add(agv_steps[idx1] + 2 <= agv_steps[idx2])  
        self.agv_steps= agv_steps 
        self.offsets_var=[model.NewConstant(self.offsets[i]) for i in range(self.machines_count)]
        # assert len(offsets_var)==self.machines_count

    def optimize(self,max_solve_time=20,pause_time=0.16):
        model=self.model
        all_machines = range(self.machines_count)
        min_x, max_x = self.min_x, self.max_x
        self.init_agvs_pos()
        
        # Creates job intervals and add to the corresponding machine lists.
        all_tasks = {}
        machine_usages = {}  # indexed by (job_id, task_id, machine_id)
        machine_to_intervals = defaultdict(list)
        for job_id, job in enumerate(self.jobs):
            for task_id, task in enumerate(job):
                suffix = "_%i_%i" % (job_id, task_id)
                duration_var = model.NewConstant(task[0].duration)
                if task_id%2==1:
                    duration_var = model.NewIntVar(0,max_x-min_x+self.agv_up_time+self.agv_down_time, f"duration{suffix}")
                
                start_var = model.NewIntVar(0, self.horizon , f"start{suffix}")
                end_var = model.NewIntVar(0, self.horizon, f"end{suffix}")
                interval_var = model.NewIntervalVar(
                    start_var, duration_var, end_var, f"interval{suffix}"
                )
                machine_var = model.NewIntVar(
                    0, self.machines_count-1, f"machine{suffix}"
                )
                # add to all_tasks
                all_tasks[job_id, task_id] = task_type(
                    start=start_var, end=end_var, interval=interval_var,machine=machine_var
                )

                # add conditional (alternative) machine intervals (only one of all machines is used)
                alt_machine_usages = []
                for alt_id, alt in enumerate(task):
                    alternative_suffix = f"{job_id}_{task_id}_{alt_id}"
                    machine_usage = model.NewBoolVar(f"presence_{alternative_suffix}")
                    alt_start = model.NewIntVar(0, self.horizon, f"start_{alternative_suffix}")
                    alt_end = model.NewIntVar(0, self.horizon, f"end_{alternative_suffix}")
                    # Link the master variables with the local ones
                    model.Add(machine_var == alt.machine).OnlyEnforceIf(machine_usage)
                    model.Add(start_var == alt_start).OnlyEnforceIf(machine_usage)
                    model.Add(end_var == alt_end).OnlyEnforceIf(machine_usage)
                    machine_usages[(job_id, task_id, alt_id)] = machine_usage
                    alt_duration = self.check_agv(machine_usage, all_tasks, job_id, task_id,alt, \
                                                duration_var,model.NewConstant(alt.duration), alt_start)
                    model.Add(alt_duration == duration_var).OnlyEnforceIf(machine_usage)
                    alt_interval = model.NewOptionalIntervalVar(
                        alt_start,
                        alt_duration,
                        alt_end,
                        machine_usage,
                        f"interval_{alternative_suffix}",
                    )
                    
                    machine_to_intervals[alt.machine].append(alt_interval)
                    alt_machine_usages.append(machine_usage)
                # select exactly one machine usage per task
                model.AddExactlyOne(alt_machine_usages)  # model.Add(sum(alt_machine_usages) == 1)

        # Create and add disjunctive constraints of intervals, in which a machine or tool may be used
        for machine in all_machines:
            model.AddNoOverlap(machine_to_intervals[machine])

        # Precedences inside a job.
        for job_id, job in enumerate(self.jobs):
            for task_id in range(len(job) - 1):
                model.Add(
                    all_tasks[job_id, task_id + 1].start >= all_tasks[job_id, task_id].end
                )
        obj_var = model.NewIntVar(0, self.horizon, "makespan")
        model.AddMaxEquality(
            obj_var,
            [all_tasks[job_id, len(job) - 1].end for job_id, job in enumerate(self.jobs)],
        )
        model.Minimize(obj_var)

        # Solve model.
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max_solve_time
        solution_printer = SolutionPrinter()
        status = solver.Solve(model, solution_printer) 
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("Solve status: %s" % solver.StatusName(status))
            print("Optimal objective value: %i" % solver.ObjectiveValue())
            data = get_assigned(self.jobs, all_tasks, solver, machine_usages)
            view_solution(self.offsets, data)
            self.replay(solver,data,pause_time)
        else:
            print("Not found solution!")

    def check_agv(self, machine_usage,all_tasks, job_id, task_id, alt, \
                duration_var,alt_duration, alt_start):
        model=self.model
        min_x, max_x=self.min_x, self.max_x
        offsets_var=self.offsets_var
        rt=alt_duration
        time_step=model.NewIntVar(0, self.horizon*self.agv_num,'')
        cur_machine_x=model.NewIntVar(min_x,max_x,'')
        model.AddElement(alt.machine,offsets_var,cur_machine_x)
        agv_x=model.NewIntVar(min_x,max_x,'')
        if task_id%2==1:# AGV开始作业位置是前一加工机器的位置
            rt=duration_var
            agv_index=alt.machine-self.agv_start
            model.Add(time_step == agv_index*self.horizon+alt_start).OnlyEnforceIf(machine_usage)
            pre_machine=all_tasks[job_id, task_id-1].machine
            pre_machine_x=model.NewIntVar(min_x,max_x,'')
            model.AddElement(pre_machine,offsets_var,pre_machine_x)
            model.AddElement(time_step,self.agv_steps,agv_x)
            model.Add(agv_x==pre_machine_x).OnlyEnforceIf(machine_usage)
        elif task_id>0:# 当前电镀处理位置是AGV结束作业位置
            agv_task=all_tasks[job_id, task_id-1]
            pre_op_task=all_tasks[job_id, task_id-2]
            agv_index=agv_task.machine-self.agv_start
            model.Add(time_step == agv_index*self.horizon+agv_task.end).OnlyEnforceIf(machine_usage)
            model.AddElement(time_step,self.agv_steps,agv_x)
            model.Add(agv_x==cur_machine_x).OnlyEnforceIf(machine_usage)
                    
            #AGV运输时间
            pre_machine_x=model.NewIntVar(min_x,max_x,'')
            model.AddElement(pre_op_task.machine,offsets_var,pre_machine_x)
            dis=model.NewIntVar(0,max_x-min_x,'')
            model.AddAbsEquality(dis,cur_machine_x-pre_machine_x)
            model.Add(agv_task.end-agv_task.start==dis+self.agv_down_time+self.agv_up_time).OnlyEnforceIf(machine_usage)

            for i in range(1,1+self.agv_up_time):
                p = model.NewIntVar(min_x, max_x, "")
                tp = model.NewIntVar(0, self.horizon*self.agv_num, "")
                model.Add(tp == agv_index*self.horizon+agv_task.start+i).OnlyEnforceIf(machine_usage)
                model.AddElement(tp,self.agv_steps,p)
                model.Add(p==pre_machine_x).OnlyEnforceIf(machine_usage)

            for i in range(1,1+self.agv_down_time):
                p = model.NewIntVar(min_x, max_x, "")
                tp = model.NewIntVar(0, self.horizon*self.agv_num, "")
                model.Add(tp == agv_index*self.horizon+agv_task.end-i).OnlyEnforceIf(machine_usage)
                model.AddElement(tp,self.agv_steps,p)
                model.Add(p==cur_machine_x).OnlyEnforceIf(machine_usage)

        return rt    

    def get_agvs_pos(self,solver,data)->Tuple[Dict[int,List[int]],Dict[int,List[int]]]:
        rt=defaultdict(list)
        n=int(solver.ObjectiveValue())
        for i in range(self.agv_num):
            for t in range(n):
                x=solver.Value(self.agv_steps[i*self.horizon+t])
                rt[i].append(x)
        rt2={}
        for i in range(self.agv_num):
            agv_idx=i+self.agv_start
            ds:List[assigned_task_type]=data[agv_idx]
            ts=[(d.start,d.start+d.duration) for  d in ds]
            rt2[i]=get_crane_states(rt[i],ts)
        return rt,rt2
    
    def print_info(self,info):
        console.print('',end='\r')
        for s in info:
            console.print(s,end='')
    def replay(self,solver,data,pause_time):
        agvs_pos,flags=self.get_agvs_pos(solver,data)
        n=len(agvs_pos[0])
        info=[Text(f'{i:^4d}', style="bold yellow") for i in range(self.min_x,self.max_x+1)]
        self.print_info(info)
        console.print()
        for t in range(n):
            info=[' '*4]*(self.max_x-self.min_x+1)
            #assert len(info)==self.max_x-self.min_x+1
            
            for k,x in enumerate(self.offsets):
                if k>=self.agv_start:
                    continue
                m=f'M{k+1}'
                s=Text(f'{m:4s}', style="bold green")
                info[x]=s
            #console.print(f'\r{info}',end='')

            for agv in range(self.agv_num):
                x=agvs_pos[agv][t]
                dir=flags[agv][t]
                m=f'{agv+1}{dir}'
                info[x]=s=Text(f'{m:4s}', style="red")
            # info=''.join(info)
            # console.print(f'\r{info}',end='')
            self.print_info(info)
            time.sleep(pause_time) 










