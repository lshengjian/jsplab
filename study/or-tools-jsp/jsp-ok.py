import collections
from ortools.sat.python import cp_model

wait_time= 1  # 3-second interval

def main() -> None:
    """Modified jobshop problem with 3-second intervals between tasks on the same machine."""
    # Data.
    jobs_data = [  # task = (machine_id, processing_time).
        [(0, 30), (1, 20), (2, 20)],  # Job0
        [(0, 20), (2, 10), (1, 40)],  # Job1
        [(1, 40), (2, 30)],  # Job2
    ]

    machines_count = 1 + max(task[0] for job in jobs_data for task in job)
    all_machines = range(machines_count)
    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(task[1] for job in jobs_data for task in job)

    # Create the model.
    model = cp_model.CpModel()

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple("task_type", "start end interval")
    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple(
        "assigned_task_type", "start job index duration"
    )

    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    machine_to_intervals = collections.defaultdict(list)

    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine, duration = task
            suffix = f"_{job_id}_{task_id}"
            start_var = model.new_int_var(0, horizon, "start" + suffix)
            end_var = model.new_int_var(0, horizon, "end" + suffix)
            interval_var = model.new_interval_var(
                start_var, duration, end_var, "interval" + suffix
            )
            all_tasks[(job_id, task_id)] = task_type(
                start=start_var, end=end_var, interval=interval_var
            )
            machine_to_intervals[machine].append(all_tasks[(job_id, task_id)])

    # Create and add disjunctive constraints.
    for machine in all_machines:
        model.add_no_overlap([task.interval for task in machine_to_intervals[machine]])

    # Add 3-second intervals between tasks on the same machine.
    handle_tasks_same_machine(all_machines, model, machine_to_intervals)

    # Precedences inside a job.
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            model.add(all_tasks[(job_id, task_id + 1)].start >= all_tasks[(job_id, task_id)].end)

    # Makespan objective.
    obj_var = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(
        obj_var,
        [all_tasks[(job_id, len(job) - 1)].end for job_id, job in enumerate(jobs_data)],
    )
    model.minimize(obj_var)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Solution:")
        # Create one list of assigned tasks per machine.
        assigned_jobs = make_assigned(jobs_data, assigned_task_type, all_tasks, solver)

        # Create per machine output lines.
        print_reslut(all_machines, solver, assigned_jobs)
    else:
        print("No solution found.")

    # Statistics.
    print("\nStatistics")
    print(f"  - conflicts: {solver.num_conflicts}")
    print(f"  - branches : {solver.num_branches}")
    print(f"  - wall time: {solver.wall_time}s")

def print_reslut(all_machines, solver, assigned_jobs):
    output = ""
    for machine in all_machines:
            # Sort by starting time.
        assigned_jobs[machine].sort()
        sol_line_tasks = "Machine " + str(machine) + ": "
        sol_line = "           "

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

        # Finally print the solution found.
    print(f"Optimal Schedule Length: {solver.objective_value}")
    print(output)

def make_assigned(jobs_data, assigned_task_type, all_tasks, solver):
    assigned_jobs = collections.defaultdict(list)
    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine = task[0]
            assigned_jobs[machine].append(
                    assigned_task_type(
                        start=solver.value(all_tasks[(job_id, task_id)].start),
                        job=job_id,
                        index=task_id,
                        duration=task[1],
                    )
                )
            
    return assigned_jobs

def handle_tasks_same_machine(all_machines, model, machine_to_intervals):
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
                    tasks[j].start >= tasks[i].end + wait_time
                ).only_enforce_if(lit)

        model.add_circuit(arcs)

if __name__ == "__main__":
    main()