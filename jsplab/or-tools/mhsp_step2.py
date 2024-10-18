from ortools.sat.python import cp_model
from collections import defaultdict,namedtuple
import matplotlib.pyplot as plt
Op=namedtuple('Op','hoist from_tank to_tank move_time op_time')
# Named tuple to store information about created variables.
task_type = namedtuple("task_type", "start end interval")
# Named tuple to manipulate solution information.
assigned_task_type = namedtuple(
    "assigned_task_type", "start job index duration from_tank to_tank"
)
# 创建模型
model = cp_model.CpModel()

#   0   1   2   3   4   5   6   7   8   9
#   S|E             X   X           Y   Y
#   |<----------T0----->|
#                   |<------T1--------->|
#   pos(T1)>=pos(T0)+2
tanks=[0,4,5,8,9]
steps=[(4,5),(8,9),(4,5),(0,)]
up_time=2
down_time=2
W=up_time+down_time
data=[
    [Op(0, 0,4,4+W,10),Op(0, 0,5,9,10)],  #Step1 S->X by T0 move_time:4 up_time:2 down_time:2 op_time:10
    [Op(1, 4,8,4+W,30),Op(1, 4,9,9,30),Op(1, 5,8,7,30),Op(1, 5,9,8,30)],  #Step2 X->Y by T1
    [Op(1, 8,4,4+W,12),Op(1, 8,5,7,12),Op(1, 9,5,8,12),Op(1, 9,4,9,12)],  #Step3 Y->X by T1
    [Op(0, 4,0,4+W,0 ),Op(0, 5,0,9,0) ]   #Step4 X->E by T0
]
jobs=[data]*2

num_hoists = 2
all_hoists = range(num_hoists)

horizon =2* sum(task[0].move_time+task[0].op_time  for task in data) #18+38+20+8=84
# 定义时间范围
print(horizon )
hoists_pos = defaultdict(list)
for t in range(horizon+1):
    for i in range(num_hoists):
        if t==0:
            hoists_pos[0].append(model.new_constant(0))
            hoists_pos[1].append(model.new_constant(7))
        else:
            hoists_pos[i].append(model.NewIntVar(0, 9, f'x_{i}_{t}'))


# 添加安全距离约束
for t in range(horizon+1):
    for i in range(0,num_hoists):
        if i>0:
            model.add(hoists_pos[i][t]>=hoists_pos[i-1][t]+2)
        if t>0:
            dx=model.NewIntVar(0,9,'')
            model.add_abs_equality(dx,hoists_pos[i][t-1]-hoists_pos[i][t])
            model.add(dx<=1)


hoist_tasks = {}
hoist_to_intervals = defaultdict(list)
hoist_keys=defaultdict(list)
tank_tasks = {}
tank_to_intervals = defaultdict(list)
tank_keys=defaultdict(list)
for job_id, job in enumerate(jobs):
    for task_id, task in enumerate(job):
        hoist,from_tank,to_tank,move_time,op_time = task[0]
        suffix = f"_{job_id}_{task_id}"
        start_var = model.new_int_var(0, horizon, "start" + suffix)
        for i in range(up_time):
            x=model.new_int_var(0, 9, '')
            temp=model.new_int_var(0, horizon, '')
            model.add(temp==start_var+i)
            model.add_element(temp,hoists_pos[hoist],x)
            model.add(x==from_tank)
        for i in range(1,1+move_time-W):
            x=model.new_int_var(0, 9, '')
            temp=model.new_int_var(0, horizon, '')
            model.add(temp==start_var+up_time+i)
            model.add_element(temp,hoists_pos[hoist],x)
            dir =1 if to_tank>from_tank else -1
            model.add(x==from_tank+dir*i)  
        end_var = model.new_int_var(0, horizon, "end" + suffix)
        for i in range(down_time):
            x=model.new_int_var(0, 9, '')
            temp=model.new_int_var(0, horizon, '')
            model.add(temp==end_var-i)
            model.add_element(temp,hoists_pos[hoist],x)
            model.add(x==to_tank)
  
        interval_var = model.new_interval_var(
            start_var, move_time, end_var, "interval" + suffix
        )
        hoist_keys[hoist].append((job_id,task_id))
        hoist_tasks[job_id,task_id] = task_type(
            start=start_var, end=end_var, interval=interval_var
        )
        hoist_to_intervals[hoist].append(interval_var)
        #hoist_keys[hoist]=job_id,task_id
        # cnt=len(hoist_ends[hoist])
        # if cnt>1:
        #     for k in range(cnt-1):
        #         ei=hoist_ends[hoist][k]
        #         temp=model.new_int_var(-100, 100, '')
        #         model.add_abs_equality(temp,ei-start_var)
        #         model.add(temp>=2*W)

        start_var=end_var
        end_var = model.new_int_var(0, horizon, "end2" + suffix)
        interval_var = model.new_interval_var(
            start_var, op_time, end_var, "interval2" + suffix
        )
        tank_keys[to_tank].append((job_id,task_id))

        tank_tasks[job_id,task_id] = task_type(
            start=start_var, end=end_var, interval=interval_var
        )
        tank_to_intervals[to_tank].append(interval_var)
        
        # cnt=len(tank_keys[to_tank])
        # if cnt>1:
        #     for k in range(cnt-1):
        #         key=tank_keys[to_tank][k]
        #         temp1=model.new_int_var(-100, 100, '')
        #         temp2=model.new_int_var(-100, 100, '')
        #         model.add_abs_equality(temp1,tank_tasks[key].end-start_var)
        #         model.add_abs_equality(temp2,end_var-tank_tasks[key].start)
        #         model.add(temp1>=1)
        #         model.add(temp2>=1)
for machine in all_hoists:
    model.add_no_overlap(hoist_to_intervals[machine])
# arcs = []
# for j1 in range(len(hoist_keys)):
#     # Initial arc from the dummy node (0) to a task.
#     start_lit = model.new_bool_var(f"{j1} is first job")
#     arcs.append((0, j1 + 1, start_lit))
#     # Final arc from an arc to the dummy node.
#     arcs.append((j1 + 1, 0, model.new_bool_var(f"{j1} is last job")))

#     for j2 in range(len(hoist_keys)):
#         if j1 == j2:
#             continue

#         lit = model.new_bool_var(f"{j2} follows {j1}")
#         arcs.append((j1 + 1, j2 + 1, lit))
#         t1=hoist_tasks[hoist_keys[j1]].end
#         t2=hoist_tasks[hoist_keys[j2]].start

        
#         model.add(
#             t2 >= t1 + 3
#         ).only_enforce_if(lit)

# model.add_circuit(arcs)    


for machine in tanks:
    model.add_no_overlap(tank_to_intervals[machine])

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
model.minimize(obj_var)

solver = cp_model.CpSolver()
status = solver.solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Solution:")
    # Create one list of assigned tasks per machine.
    assigned_hoists =defaultdict(list)
    assigned_tanks =defaultdict(list)
    for job_id, job in enumerate(jobs):
        for task_id, task in enumerate(job):
            hoist,from_tank,to_tank,move_time,op_time = task[0]
            assigned_hoists[hoist].append(
                assigned_task_type(
                    start=solver.value(hoist_tasks[job_id, task_id].start),
                    job=job_id,
                    index=task_id,
                    duration=move_time,
                    from_tank=from_tank,
                    to_tank=to_tank
                )
            )
            if to_tank==0:
                continue
            assigned_tanks[to_tank].append(
                assigned_task_type(
                    start=solver.value(tank_tasks[job_id, task_id].start),
                    job=job_id,
                    index=task_id,
                    duration=op_time,
                    from_tank=from_tank,
                    to_tank=to_tank
                )
            )

    # Create per machine output lines.
    output = ""
    for machine in all_hoists:
        # Sort by starting time.
        assigned_hoists[machine].sort()
        sol_line_tasks = "H" + str(machine+1) + ": "
        sol_line = " "*4

        for assigned_task in assigned_hoists[machine]:
            name = f"j{assigned_task.job+1}-{assigned_task.index+1}"
            # add spaces to output to align columns.
            sol_line_tasks += f"{name:8}"

            start = assigned_task.start
            duration = assigned_task.duration
            sol_tmp = f"[{assigned_task.from_tank}|{assigned_task.to_tank} {start}->{start + duration}]"
            # add spaces to output to align columns.
            sol_line += f"{sol_tmp:8}"

        sol_line += "\n"
        sol_line_tasks += "\n"
        output += sol_line_tasks
        output += sol_line
    output += '-'*6+'\n'
    for machine in tanks:
        # Sort by starting time.
        assigned_tanks[machine].sort()
        sol_line_tasks = "T" + str(machine) + ": "
        sol_line = " "*4

        for assigned_task in assigned_tanks[machine]:
            name = f"j{assigned_task.job+1}-{assigned_task.index+1}"
            # add spaces to output to align columns.
            sol_line_tasks += f"{name:8}"

            start = assigned_task.start
            duration = assigned_task.duration
            sol_tmp = f"[{start}->{start + duration}]"
            # add spaces to output to align columns.
            sol_line += f"{sol_tmp:8}"

        sol_line += "\n"
        sol_line_tasks += "\n"
        output += sol_line_tasks
        output += sol_line
    # Finally print the solution found.
    print(f"Optimal Schedule Length: {solver.objective_value}")
    print(output)
    H1 = [solver.Value(pos) for pos in hoists_pos[0]]
    H2 = [solver.Value(pos) for pos in hoists_pos[1]]
    # for t in range(60):
    #     print(f'{t:2} {H1[t]:2}|{H2[t]:2}')

    # x = range(len(H1))
    # plt.plot(x, H1, label='H1')
    # plt.plot(x, H2, label='H2')
    # plt.xlabel('Index')
    # plt.ylabel('Value')
    # plt.title('Visualization of Two Crane Positions')
    # plt.legend()
    # plt.show()
else:
    print("No solution found.")


