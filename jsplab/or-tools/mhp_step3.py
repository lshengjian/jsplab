from ortools.sat.python import cp_model
from collections import defaultdict,namedtuple
import matplotlib.pyplot as plt
up_time=2
down_time=2
W=up_time+down_time
num_jobs=1
Op=namedtuple('Op','hoist move_time from_tank to_tank  op_time')
# Named tuple to store information about created variables.
task_type = namedtuple("task_type", "start end interval")
# Named tuple to manipulate solution information.
assigned_task_type =namedtuple(
    "assigned_task_type", "start job index duration"
)
def main() -> None:
    """Modified jobshop problem with 3-second intervals between tasks on the same machine."""

    #   0   1   2   3   4   5   6   7   8   9
    #   S|E             X   X           Y   Y
    #   |<----------T0----->|
    #                   |<------T1--------->|
    #   pos(T1)>=pos(T0)+2

    tanks=[0,2,3,6]
    #steps=[(4,5),(8,9)]#,(4,5),(0,)
    # OP1 T2 time: 12（6~18） OP2 T3 time:16（15~31）
    data=[
        Op(0, 2+W,0,2,12), 
        Op(0, 3+W,0,3,16),
        Op(1, 4+W,2,6,0),
        Op(1, 3+W,3,6,0), 
    ]
    # data=[
    #     Op(0, 3+W,0,3,10),  #Step1 S->X by T0 move_time:8 op_time:10
    #     Op(1, 3+W,3,6,30),  #Step2 X->Y by T1
    #     Op(1, 2+W,6,4,10),  #Step3 Y->X by T1
    #     Op(0, 4+W,4,0,0 )   #Step4 X->E by T0
    # ]
    jobs=[data]*num_jobs
    num_hoists = 2
    all_hoists = range(num_hoists)
    for d in data:
        print(d.move_time,d.op_time)
    horizon =(num_jobs)* sum(task.move_time+task.op_time  for task in data) #19+38+21+8=86
    horizon+=len(data)*(1+W)

    print(horizon )

    # Create the model.
    model = cp_model.CpModel()

    hoists_pos = defaultdict(list)
    hoists_steps = defaultdict(list)
    for t in range(horizon):
        for i in range(num_hoists):
            if t==0 or t==horizon-1:
                hoists_pos[0].append(model.new_constant(0))
                hoists_pos[1].append(model.new_constant(7))
            else:
                hoists_pos[i].append(model.NewIntVar(0, 9, f'x_{i}_{t}'))

    # 添加安全距离约束
    for t in range(horizon):
        for i in range(0,num_hoists):
            # if i>0:
            #     model.add(hoists_pos[i][t]>hoists_pos[i-1][t]+1)
            if t>0:
                dx=model.NewIntVar(0,9,'')
                model.add_abs_equality(dx,hoists_pos[i][t-1]-hoists_pos[i][t])
                model.add(dx<=1)
                hoists_steps[i].append(dx)
    cumulative_var = cp_model.LinearExpr.Sum(hoists_steps[0]+hoists_steps[1])
    hoist_tasks = defaultdict(list)
    hoist_vars = defaultdict(list)
    tank_tasks = defaultdict(list)
    tank_vars = defaultdict(list)


    for job_id, job in enumerate(jobs):
        for task_id, task in enumerate(job):
            hoist,move_time,from_tank,to_tank,op_time = task
            suffix = f"_{job_id}_{task_id}"
            start_var = model.new_int_var(0, horizon, "start" + suffix)
            
            x=model.new_int_var(0, 9, '')
            temp=model.new_int_var(0, horizon, '')
            model.add(temp==start_var)
            model.add_element(temp,hoists_pos[hoist],x)
            model.add(x==from_tank)
            for i in range(up_time,move_time-W+up_time-1):
                x=model.new_int_var(0, 9, '')
                temp=model.new_int_var(0, horizon, '')
                model.add(temp==start_var+i)
                model.add_element(temp,hoists_pos[hoist],x)
                dir =1 if to_tank>from_tank else -1
                model.add(x==from_tank+dir*i)  
            end_var = model.new_int_var(0, horizon, "end" + suffix)
            interval_var = model.new_interval_var(
                start_var, move_time, end_var, "interval" + suffix
            )
            x=model.new_int_var(0, 9, '')
            temp=model.new_int_var(0, horizon, '')
            model.add(temp==end_var)
            model.add_element(temp,hoists_pos[hoist],x)
            model.add(x==to_tank)


            hoist_tasks[job_id,task_id]=task_type(
                start=start_var, end=end_var, interval=interval_var
            )

            hoist_vars[hoist].append(hoist_tasks[job_id,task_id])

            start_var=end_var
            end_var = model.new_int_var(0, horizon, "end2" + suffix)

            interval_var = model.new_interval_var(
                start_var, op_time, end_var, "interval2" + suffix
            )


            tank_tasks[job_id,task_id]=task_type(
                start=start_var, end=end_var, interval=interval_var
            )
            tank_vars[to_tank].append(tank_tasks[job_id,task_id])

    handle_tasks_same_machine( model, hoist_vars)
    handle_tasks_same_machine( model, tank_vars,False)
    for h in all_hoists:
        model.add_no_overlap([task.interval for task in hoist_vars[h]])
    for tank in tanks:
        model.add_no_overlap([task.interval for task in tank_vars[tank]])

    for job_id, job in enumerate(jobs):
        for task_id in range(len(job) - 1):
            model.add(
                hoist_tasks[job_id,task_id + 1].start == tank_tasks[job_id,task_id].end
            )



    # Makespan objective.
    obj_var = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(
        obj_var,
        [tank_tasks[job_id,task_id].end for task_id, _ in enumerate(job) for job_id, job in enumerate(jobs)]
    )
    
    model.minimize(obj_var+cumulative_var)#

    solver = cp_model.CpSolver()
    status = solver.solve(model)


    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Solution:")
            # Finally print the solution found.
        print(f"Optimal:{solver.value(obj_var)}/ {solver.objective_value}")
        # Create one list of assigned tasks per machine.
        hoist_assigned_jobs,tank_assigned_jobs = make_assigned(solver,jobs,  hoist_tasks,  tank_tasks)

        # Create per machine output lines.
        print_reslut(solver, hoist_assigned_jobs)
        print_reslut(solver, tank_assigned_jobs,False)
        H1 = [solver.Value(pos) for pos in hoists_pos[0]]
        H2 = [solver.Value(pos) for pos in hoists_pos[1]]
        # for t in range(60):
        #     print(f'{t:2} {H1[t]:2}|{H2[t]:2}')

        x = range(len(H1))
        plt.plot(x, H1, label='H1')
        plt.plot(x, H2, label='H2')
        plt.xlabel('Index')
        plt.ylabel('Value')
        plt.title('Visualization of Two Crane Positions')
        plt.legend()
        plt.show()
    else:
        print("No solution found.")



def print_reslut( solver, assigned_jobs,is_hoist=True):
    output = ""
    machines=list(assigned_jobs.keys())
    machines.sort()
    for machine in machines:
            # Sort by starting time.
        assigned_jobs[machine].sort()
        sol_line_tasks = "Hoist " + str(machine+1) + ": " if is_hoist else "Tank " + str(machine) + ": " 
        sol_line = "         "

        for assigned_task in assigned_jobs[machine]:
            name = f"j{assigned_task.job+1}_{assigned_task.index+1}"
                # add spaces to output to align columns.
            sol_line_tasks += f"{name:15}"

            start = assigned_task.start
            duration = assigned_task.duration
            sol_tmp = f"[{start},{start + duration}]"
                # add spaces to output to align columns.
            sol_line += f"{sol_tmp:15}"

        sol_line += "\n"
        sol_line_tasks += "\n"
        output += sol_line_tasks
        output += sol_line

    
    print(output)

def make_assigned(solver,jobs_data,  hoist_tasks,tank_tasks ):
    hoist_assigned_jobs = defaultdict(list)
    tank_assigned_jobs = defaultdict(list)
    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            hoist,move_time,from_tank,to_tank,op_time = task
            
            hoist_assigned_jobs[hoist].append(
                    assigned_task_type(
                        start=solver.value(hoist_tasks[(job_id, task_id)].start),
                        job=job_id,
                        index=task_id,
                        duration=move_time,
                    )
                )
            tank_assigned_jobs[to_tank].append(
                    assigned_task_type(
                        start=solver.value(tank_tasks[(job_id, task_id)].start),
                        job=job_id,
                        index=task_id,
                        duration=op_time,
                    )
                )
            
    return hoist_assigned_jobs,tank_assigned_jobs

def handle_tasks_same_machine( model, machine_to_intervals,is_hoist=True):
    all_machines=machine_to_intervals.keys()
    step=2 if is_hoist else W
    for machine in all_machines:
        tasks = machine_to_intervals[machine]
        arcs = []
        for i in range(len(tasks)):
            # Initial arc from the dummy node (0) to a task.
            start_lit = model.new_bool_var(f"task_{i} is first job")
            arcs.append((0, i + 1, start_lit))
            # Final arc from a task to the dummy node.
            end_lit = model.new_bool_var(f"task_{i} is last job")
            arcs.append((i + 1, 0, end_lit))

            for j in range(len(tasks)):
                if i == j:
                    continue

                lit = model.new_bool_var(f"task_{j} follows task_{i}")
                arcs.append((i + 1, j + 1, lit))

                model.add(
                    tasks[j].start >= tasks[i].end + step
                ).only_enforce_if(lit)

        model.add_circuit(arcs)

if __name__ == "__main__":
    main()