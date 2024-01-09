"""Minimal jobshop example."""
import collections
from ortools.sat.python import cp_model
import time
from typing import List
import matplotlib
import numpy as np
import pandas as pd
from jsplab import JSP_Data
from jsplab.utils.gantt import Visualizer
machine_offsets=[1,4,7]
agv_offsets=[4]
agv_up_time=1
agv_down_time=1
agv_safe_distance=2

def simulate(solver,agv_pos):
    # machines_pos=machine_offsets
    n=int(solver.ObjectiveValue())
    info=[str(i) for i in range(1,10)]
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

 

def slove(ins_data:JSP_Data):
    num_agv=len(agv_offsets)
    min_pos=min(machine_offsets)
    max_pos=max(machine_offsets)
    jobs_data =ins_data.jobs_data

    machines_count = 1 + max(task.machine for job in jobs_data for task in job)
    total_tasks=sum([len(job) for job in jobs_data])
    all_machines = range(machines_count)
    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(task.duration for job in jobs_data for task in job)
    up_down=agv_up_time+agv_down_time
    up_time=agv_up_time
    down_time=agv_down_time

    horizon +=total_tasks*(up_down+(max_pos-min_pos))

    model = cp_model.CpModel()

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple("task_type", "start end interval")
    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple(
        "assigned_task_type", "start job index duration"
    )
    agv_history={}
    for idx,x in enumerate(agv_offsets):
        agv_history[idx]=[model.NewConstant(x)]
        for i in range(horizon-1):
            agv_pos=agv_history[idx]
            agv_pos.append(model.NewIntVar(min_pos, max_pos, f"agv_{idx}_{i}"))
            p1 = agv_pos[i]
            p2 = agv_pos[i+1]
            temp=model.NewIntVar(0, 1, "") 
            model.AddAbsEquality(temp,p1-p2)

    for t in range(horizon):
        for idx,x in enumerate(agv_offsets):
            if idx>=num_agv-1:
                continue
            model.Add(agv_history[idx][t]+agv_safe_distance<=agv_history[idx+1][t])
    
    # Creates job intervals and add to the corresponding machine lists.
    all_tasks ={}
    
    machine_to_intervals = collections.defaultdict(list)
    agv_to_intervals = collections.defaultdict(list)

    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine, duration = task
            suffix = f"_{job_id}_{task_id}"
            start_var = model.NewIntVar(0, horizon, "start" + suffix)
            end_var = model.NewIntVar(0, horizon, "end" + suffix)
            interval_var = model.NewIntervalVar(
                start_var, duration, end_var, "interval" + suffix
            )
            all_tasks[job_id, task_id] = task_type(
                start=start_var, end=end_var, interval=interval_var
            )
            machine_to_intervals[machine].append(interval_var)

    # Create and add disjunctive constraints.
    for machine in all_machines:
        model.AddNoOverlap(machine_to_intervals[machine])

    # Precedences inside a job.
    agv_pos=agv_history[0]
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            task1 = job[task_id]
            task2 = job[task_id+1]
            plan1=all_tasks[job_id, task_id]
            plan2=all_tasks[job_id, task_id+1]
            #print(machines_pos[machine1],machines_pos[machine2])

            p1 = model.NewIntVar(1, 9, "")
            model.AddElement(plan1.end,agv_pos,p1)
            model.Add(p1==machine_offsets[task1.machine])
            for k in range(1,up_time+1):
                p = model.NewIntVar(1, 9, "")
                tp = model.NewIntVar(0, horizon, "")
                model.Add(tp==plan1.end+k)
                model.AddElement(tp,agv_pos,p)
                model.Add(p==machine_offsets[task1.machine])

            p2 = model.NewIntVar(1, 9, "")
            model.AddElement(plan2.start,agv_pos,p2)
            model.Add(p2==machine_offsets[task2.machine])
            
            for k in range(1,down_time+1):
                p = model.NewIntVar(1, 9, "")
                tp = model.NewIntVar(0, horizon, "")
                model.Add(tp==plan2.start-k)
                model.Add(tp>0)
                model.AddElement(tp,agv_pos,p)
                model.Add(p==machine_offsets[task2.machine])
        
            move_time=model.NewIntVar(1, 9, "") 
            model.AddAbsEquality(move_time,p1-p2)
            model.Add(
                plan2.start >= plan1.end+move_time+up_time+down_time
            )
            suffix = f"_agv_{job_id}_{task_id}"
            interval_var = model.NewIntervalVar(
                plan1.end,up_time+move_time+down_time, plan2.start,  "interval" + suffix
            )
            if task_id==0:
                agv_to_intervals[0].append(interval_var)
            else:
                agv_to_intervals[num_agv-1].append(interval_var)


    for agv in range(len(agv_offsets)):
        model.AddNoOverlap(agv_to_intervals[agv])
    # Makespan objective.
    obj_var = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(
        obj_var,
        [all_tasks[job_id, len(job) - 1].end for job_id, job in enumerate(jobs_data)],
    )
    model.Minimize(obj_var)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Create one list of assigned tasks per machine.
        assigned_jobs = collections.defaultdict(list)
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                machine = task.machine
                assigned_jobs[machine].append(
                    assigned_task_type(
                        start=solver.Value(all_tasks[job_id, task_id].start),
                        job=job_id,
                        index=task_id,
                        duration=task.duration,
                    )
                )

        # Create per machine output lines.

        c_map = matplotlib.colormaps["rainbow"]
        arr = np.linspace(0, 1, machines_count, dtype=float)
        machine_colors = {m_id: c_map(val)  for m_id, val in enumerate(arr)}
        colors = {f"M_{m_id+1}": (r, g, b) for m_id, (r, g, b, a) in machine_colors.items()}
        
        df=pd.DataFrame([
                {
                    'Task': f'J{task.job+1}',
                    'Start': task.start,
                    'Finish': task.start+task.duration,
                    'Resource': f'M_{machine+1}'
                }
                for machine, data in assigned_jobs.items() for task in data
            ])

        Visualizer.gantt_chart_console(df,colors)
        simulate(solver,agv_history[0])
        print(f"Optimal Schedule Length: {solver.ObjectiveValue()}")
        print_solution(all_machines, assigned_jobs)
    else:
        print("No solution found.")

def print_solution(all_machines, assigned_jobs):
    
    output = ""
    for machine in all_machines:
            # Sort by starting time.
        assigned_jobs[machine].sort()
        x=machine_offsets[machine]
        sol_line_tasks = f"M{machine+1}[{x}]: "
        sol_line = " "*8

        for assigned_task in assigned_jobs[machine]:
            name = f"J{assigned_task.job+1}_{assigned_task.index+1}"
                # Add spaces to output to align columns.
            sol_line_tasks += f"{name:15}"

            start = assigned_task.start
            duration = assigned_task.duration
            sol_tmp = f"{start}->{start + duration}"
                # Add spaces to output to align columns.
            sol_line += f"{sol_tmp:15}"

        sol_line += "\n"
        sol_line_tasks += "\n"
        output += sol_line_tasks
        output += sol_line
    print(output)





