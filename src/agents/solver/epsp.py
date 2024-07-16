from ortools.sat.python import cp_model
from .util import *
from src.core import convert2fjsp_data
from src.core.parsers import Instance
from typing import  List
import time

def simulate(solver,agv_pos,machine_offsets):
    # machines_pos=machine_offsets
    n=int(solver.ObjectiveValue())
    info=[str(i) for i in range(0,10)]
    info=''.join(info)
    print(f'\r{info}')
    s1=''
    s2=''
    max_pos=max(machine_offsets)

    for i in range(n):
        info=list(' '*max_pos)
        
        for p in machine_offsets:
            info[p-1]='\033[0;50m'+' \033[0m'

        d=solver.Value(agv_pos[i])-1
        info[d]='\033[0;40;32m'+'o\033[0m'
        info=''.join(info)
        print(f'\r{info}',end='')
        time.sleep(0.2) 
        s1+=f'{i%10}'
        s2+=str(solver.Value(agv_pos[i]))
    print()
    print(s1)
    print(s2)

#def limit_stay(model,pos,time=2,dir=1):


def solve_epsp(info: Instance,agv_up_time=2,agv_down_time=2):
    """Solve a small ep jobshop problem."""
    machines_count = len(info.machine_offsets)
    horizon = sum(task.runtime for task in info.tasks)
    horizon+=horizon//5
    print(f"Horizon :{horizon}")

    jobs = convert2fjsp_data(info.tasks)
    all_machines = range(machines_count)
    model = cp_model.CpModel()

    offsets = info.machine_offsets
    offsets_var=[model.NewConstant(offsets[i]) for i in all_machines]
    assert len(offsets_var)==machines_count
    min_x, max_x = min(offsets), max(offsets)
    agv_start = info.first_crane_index
    agv_num = machines_count - agv_start
    agv_steps: List[cp_model.IntVar] = [None]*agv_num*horizon #把多维数组压缩为一维数组

    for agv in range(agv_num):
        agv_steps[agv*horizon]=model.NewConstant(offsets[agv_start + agv])
        for t in range(1, horizon):
            idx=agv*horizon+t
            agv_steps[idx]=model.NewIntVar(min_x, max_x, f'agv{agv}_{idx}')
            tp = model.NewIntVar(0, 1,'')
            p2 = agv_steps[idx]
            p1 = agv_steps[idx - 1]
            model.AddAbsEquality(tp, p2 - p1)  # 确保天车一个时间单位最多只移动一个位置

    # 确保天车顺序及安全距离
    for agv in range(agv_num - 1):
        for t in range(horizon):
            idx1=agv*horizon+t
            idx2=(agv+1)*horizon+t
            model.Add(agv_steps[idx1] + 2 <= agv_steps[idx2])

    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    machine_usages = {}  # indexed by (job_id, task_id, machine_id)
    machine_to_intervals = defaultdict(list)
    for job_id, job in enumerate(jobs):
        for task_id, task in enumerate(job):
            suffix = "_%i_%i" % (job_id, task_id)
            duration_var = model.NewConstant(task[0].duration)
            if task_id%2==1:
                duration_var = model.NewIntVar(0,max_x-min_x+agv_up_time+agv_down_time, f"duration{suffix}")
            
            start_var = model.NewIntVar(0, horizon , f"start{suffix}")
            end_var = model.NewIntVar(0, horizon, f"end{suffix}")
            interval_var = model.NewIntervalVar(
                start_var, duration_var, end_var, f"interval{suffix}"
            )
            machine_var = model.NewIntVar(
                0, machines_count-1, f"machine{suffix}"
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
                alt_start = model.NewIntVar(0, horizon, f"start_{alternative_suffix}")
                alt_end = model.NewIntVar(0, horizon, f"end_{alternative_suffix}")

                alt_duration=model.NewConstant(alt.duration)
                # Link the master variables with the local ones
                
                model.Add(machine_var == alt.machine).OnlyEnforceIf(machine_usage)
                model.Add(start_var == alt_start).OnlyEnforceIf(machine_usage)
                model.Add(end_var == alt_end).OnlyEnforceIf(machine_usage)
                machine_usages[(job_id, task_id, alt_id)] = machine_usage
                
                time_step=model.NewIntVar(0, horizon*agv_num,'')
                cur_machine_x=model.NewIntVar(min_x,max_x,'')
                model.AddElement(alt.machine,offsets_var,cur_machine_x)
                agv_x=model.NewIntVar(min_x,max_x,'')

                if task_id%2==1:# AGV开始作业位置是前一加工机器的位置
                    alt_duration=duration_var
                    agv_index=alt.machine-agv_start
                    model.Add(time_step == agv_index*horizon+alt_start).OnlyEnforceIf(machine_usage)
                    pre_machine=all_tasks[job_id, task_id-1].machine
                    pre_machine_x=model.NewIntVar(min_x,max_x,'')
                    
                    model.AddElement(pre_machine,offsets_var,pre_machine_x)
                    model.AddElement(time_step,agv_steps,agv_x)
                    model.Add(agv_x==pre_machine_x).OnlyEnforceIf(machine_usage)
                    

                elif task_id>0:# 当前电镀处理位置是AGV结束作业位置
                    agv_task=all_tasks[job_id, task_id-1]
                    pre_op=all_tasks[job_id, task_id-2]
                    agv_index=agv_task.machine-agv_start
                    model.Add(time_step == agv_index*horizon+agv_task.end).OnlyEnforceIf(machine_usage)
                    model.AddElement(time_step,agv_steps,agv_x)
                    model.Add(agv_x==cur_machine_x).OnlyEnforceIf(machine_usage)
                   
                    #AGV运输时间
                    pre_machine_x=model.NewIntVar(min_x,max_x,'')
                    model.AddElement(pre_op.machine,offsets_var,pre_machine_x)
                    dis=model.NewIntVar(0,max_x-min_x,'')
                    model.AddAbsEquality(dis,cur_machine_x-pre_machine_x)
                    model.Add(agv_task.end-agv_task.start>=dis+agv_down_time+agv_up_time).OnlyEnforceIf(machine_usage)

                    for i in range(1,1+agv_up_time):
                        p = model.NewIntVar(min_x, max_x, "")
                        tp = model.NewIntVar(0, horizon*agv_num, "")
                        model.Add(tp == agv_index*horizon+agv_task.start+i).OnlyEnforceIf(machine_usage)
                        model.AddElement(tp,agv_steps,p)
                        model.Add(p==pre_machine_x).OnlyEnforceIf(machine_usage)

                    for i in range(1,1+agv_down_time):
                        p = model.NewIntVar(min_x, max_x, "")
                        tp = model.NewIntVar(0, horizon*agv_num, "")
                        model.Add(tp == agv_index*horizon+agv_task.end-i).OnlyEnforceIf(machine_usage)
                        model.AddElement(tp,agv_steps,p)
                        model.Add(p==cur_machine_x).OnlyEnforceIf(machine_usage)

                model.Add(alt_duration == duration_var).OnlyEnforceIf(machine_usage)
                alt_interval = model.NewOptionalIntervalVar(
                    alt_start,
                    alt_duration,
                    alt_end,
                    machine_usage,
                    f"interval_{alternative_suffix}",
                )
                model.Add(duration_var == alt_duration).OnlyEnforceIf(machine_usage)
                machine_to_intervals[alt.machine].append(alt_interval)
                alt_machine_usages.append(machine_usage)
            # select exactly one machine usage per task
            model.AddExactlyOne(
                alt_machine_usages
            )  # model.Add(sum(alt_machine_usages) == 1)

    # Create and add disjunctive constraints of intervals, in which a machine or tool may be used
    for machine in all_machines:
        model.AddNoOverlap(machine_to_intervals[machine])

    # Precedences inside a job.
    for job_id, job in enumerate(jobs):
        for task_id in range(len(job) - 1):
            model.Add(
                all_tasks[job_id, task_id + 1].start >= all_tasks[job_id, task_id].end
            )
    obj_var = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(
        obj_var,
        [all_tasks[job_id, len(job) - 1].end for job_id, job in enumerate(jobs)],
    )
    model.Minimize(obj_var)

    # Solve model.
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = MAX_SEARCH_TIME_IN_SECONDS
    solution_printer = SolutionPrinter()
    status = solver.Solve(model, solution_printer)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Solve status: %s" % solver.StatusName(status))
        print("Optimal objective value: %i" % solver.ObjectiveValue())
        data = get_assigned(jobs, all_tasks, solver, machine_usages)
        view_solution(offsets, data)
        simulate(solver,agv_steps,offsets)
        # for i,x in enumerate(agv_steps):
        #     print(f'{i}:{solver.Value(x)}')
    else:
        print("Not found solution!")
