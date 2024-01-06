"""Minimal jobshop example."""
import collections
from ortools.sat.python import cp_model
import time
import matplotlib
import numpy as np
import pandas as pd
from jsplab import JSP_Data
from jsplab.utils.gantt import Visualizer

def demo(solver,agv_pos):
    n=int(solver.ObjectiveValue())
    info=[str(i) for i in range(1,10)]
    info=''.join(info)
    print(f'\r{info}')
    s1=''
    s2=''

    for i in range(n):
        info=list(' '*9)
        d=solver.Value(agv_pos[i])
        info[d]='\033[0;40;32m'+'o\033[0m'
        info=''.join(info)
        print(f'\r{info}',end='')
        time.sleep(0.2) 
        s1+=f'{i%10}'
        s2+=str(solver.Value(agv_pos[i]))
    print()
    print(s1)
    print(s2)
 

def slove(ins_data:JSP_Data,updown=3):
    """Minimal jobshop problem."""
    # Data.
    jobs_data =ins_data.jobs_data

    machines_count = 1 + max(task.machine for job in jobs_data for task in job)
    all_machines = range(machines_count)
    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(task.duration for job in jobs_data for task in job)
    horizon *=2



    # Create the model.
    model = cp_model.CpModel()

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple("task_type", "start end interval")
    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple(
        "assigned_task_type", "start job index duration"
    )
    agv_pos=[model.NewConstant(5)]
    for i in range(1,horizon):
        agv_pos.append(model.NewIntVar(0, 9, f"agv_{i}"))
        p1 = agv_pos[i-1]
        p2 = agv_pos[i]
        temp=model.NewIntVar(0, 1, "") 
        model.AddAbsEquality(temp,p1-p2)
        model.Add(temp<=1)
    
    
    # Creates job intervals and add to the corresponding machine lists.
    all_tasks ={}


    machine_to_intervals = collections.defaultdict(list)

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
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            machine1,_ = job[task_id]
            machine2,_ = job[task_id+1]
            p1 = model.NewIntVar(1, 9, "")
            model.AddElement(all_tasks[job_id, task_id].end,agv_pos,p1)
            model.Add(p1==machine1+1)
            for k in range(1,updown+1):
                p = model.NewIntVar(1, 9, "")
                tp = model.NewIntVar(0, horizon, "")
                model.Add(tp==all_tasks[job_id, task_id].end+k)
                model.AddElement(tp,agv_pos,p)
                model.Add(p==machine1+1)

            p2=model.NewIntVar(1, 9, "")
            model.AddElement(all_tasks[job_id, task_id + 1].start,agv_pos,p2)
            model.Add(p2==machine2+1)
            if task_id>0:
                for k in range(1,updown+1):
                    p = model.NewIntVar(1, 9, "")
                    tp = model.NewIntVar(0, horizon, "")
                    model.Add(tp==all_tasks[job_id, task_id].start-k)
                    model.AddElement(tp,agv_pos,p)
                    model.Add(p==machine2+1)
            
            dis=model.NewIntVar(1, 9, "") 
            model.AddAbsEquality(dis,p1-p2)
            model.Add(
                all_tasks[job_id, task_id + 1].start >= all_tasks[job_id, task_id].end+dis
            )

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
        output = ""
        for machine in all_machines:
            # Sort by starting time.
            assigned_jobs[machine].sort()
            sol_line_tasks = f"M-{machine+1}: "
            sol_line = " "*4

            for assigned_task in assigned_jobs[machine]:
                name = f"J{assigned_task.job+1}_{assigned_task.index+1}"
                # Add spaces to output to align columns.
                sol_line_tasks += f"{name:15}"

                start = assigned_task.start
                duration = assigned_task.duration
                sol_tmp = f"[{start},{start + duration}]"
                # Add spaces to output to align columns.
                sol_line += f"{sol_tmp:15}"

            sol_line += "\n"
            sol_line_tasks += "\n"
            output += sol_line_tasks
            output += sol_line

        # Finally print the solution found.
        print(f"Optimal Schedule Length: {solver.ObjectiveValue()}")
        print(output)
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
        demo(solver,agv_pos)
    else:
        print("No solution found.")





