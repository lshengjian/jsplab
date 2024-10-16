from ortools.sat.python import cp_model
from collections import defaultdict,namedtuple
import matplotlib.pyplot as plt
Op=namedtuple('Op','hoist from_tank to_tank move_time op_time')
# Named tuple to store information about created variables.
task_type = namedtuple("task_type", "start end interval")
# Named tuple to manipulate solution information.
assigned_task_type = namedtuple(
    "assigned_task_type", "start job index duration"
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
for t in range(horizon):
    for i in range(num_hoists):
        if t==0:
            hoists_pos[0].append(model.new_constant(0))
            hoists_pos[1].append(model.new_constant(7))
        else:
            hoists_pos[i].append(model.NewIntVar(0, 9, f'x_{i}_{t}'))


# 添加安全距离约束
for t in range(horizon):
    for i in range(0,num_hoists):
        x=model.NewIntVar(0,9,'')
        if i>0:
            model.add(hoists_pos[i][t]>=hoists_pos[i-1][t]+2)
        if t>0:
            dx=model.NewIntVar(-9,9,'')
            model.add_abs_equality(dx,hoists_pos[i][t-1]-hoists_pos[i][t])
            model.add(dx<=1)


all_tasks = {}
hoist_to_intervals = defaultdict(list)
tank_to_intervals = defaultdict(list)
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
        all_tasks[job_id,task_id,0] = task_type(
            start=start_var, end=end_var, interval=interval_var
        )
        hoist_to_intervals[hoist].append(interval_var)
        start_var=end_var
        end_var = model.new_int_var(0, horizon, "end2" + suffix)
        interval_var = model.new_interval_var(
            start_var, op_time, end_var, "interval2" + suffix
        )

        all_tasks[job_id,task_id,1] = task_type(
            start=start_var, end=end_var, interval=interval_var
        )
        tank_to_intervals[to_tank].append(interval_var)
    
for machine in all_hoists:
    model.add_no_overlap(hoist_to_intervals[machine])
for machine in tanks:
    model.add_no_overlap(tank_to_intervals[machine])

for job_id, job in enumerate(jobs):
    for task_id in range(len(job) - 1):
        model.add(
            all_tasks[job_id,task_id + 1,0].start == all_tasks[job_id,task_id ,1].end
        )


# Makespan objective.
obj_var = model.new_int_var(0, horizon, "makespan")
model.add_max_equality(
    obj_var,
    [all_tasks[job_id,task_id, 1].end for task_id, _ in enumerate(job) for job_id, job in enumerate(jobs)],
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
                    start=solver.value(all_tasks[job_id, task_id,0].start),
                    job=job_id,
                    index=task_id,
                    duration=move_time
                )
            )
            assigned_tanks[to_tank].append(
                assigned_task_type(
                    start=solver.value(all_tasks[job_id, task_id,1].start),
                    job=job_id,
                    index=task_id,
                    duration=op_time
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
            name = f"j{assigned_task.job}-{assigned_task.index}"
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
    output += '-'*6+'\n'
    for machine in tanks:
        # Sort by starting time.
        assigned_tanks[machine].sort()
        sol_line_tasks = "T" + str(machine) + ": "
        sol_line = " "*4

        for assigned_task in assigned_tanks[machine]:
            name = f"j{assigned_task.job}-{assigned_task.index}"
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
    # print('H1:', [solver.Value(pos) for pos in hoists_pos[0]])
    # print('H2:', [solver.Value(pos) for pos in hoists_pos[1]])
else:
    print("No solution found.")


H1 = [solver.Value(pos) for pos in hoists_pos[0]]
H2 = [solver.Value(pos) for pos in hoists_pos[1]]

x = range(len(H1))
plt.plot(x, H1, label='H1')
plt.plot(x, H2, label='H2')
plt.xlabel('Index')
plt.ylabel('Value')
plt.title('Visualization of Two Crane Positions')
plt.legend()
plt.show()