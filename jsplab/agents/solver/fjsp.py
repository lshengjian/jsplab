import collections
from ortools.sat.python import cp_model

from .util import *
from jsplab.core import convert2fjsp_data
from jsplab.instances.parsers import InstanceInfo



def solve_fjsp(info:InstanceInfo):
    """Solve a small flexible jobshop problem."""

    jobs=convert2fjsp_data(info.jobs)
    num_jobs = len(jobs)
    all_jobs = range(num_jobs)
    machines_count = 1 + max(op_time.machine for job in jobs for task in job for op_time in task)
    all_machines = range(machines_count)

    # Model the flexible jobshop problem.
    model = cp_model.CpModel()

    horizon = 0
    for job in jobs:
        for task in job:
            max_task_duration = 0
            for alternative in task:
                max_task_duration = max(max_task_duration, alternative.duration)
            horizon += max_task_duration

    print(f"Horizon :{horizon}"  )

    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    machine_usages = {}  # indexed by (job_id, task_id, machine_id)
    machine_to_intervals = collections.defaultdict(list)
    for job_id, job in enumerate(jobs):
        for task_id, task in enumerate(job):
            min_duration = task[0].duration
            max_duration = task[0].duration

            num_alternatives = len(task)
            for alt_id in range(1, num_alternatives):
                alt_duration = task[alt_id].duration
                min_duration = min(min_duration, alt_duration)
                max_duration = max(max_duration, alt_duration)


            suffix = '_%i_%i' % (job_id, task_id)

            start_var = model.NewIntVar(0, horizon - min_duration, f'start{suffix}')
            duration_var = model.NewIntVar(min_duration,max_duration,f'duration{suffix}')
            end_var = model.NewIntVar(0, horizon, f'end{suffix}')
            interval_var = model.NewIntervalVar(start_var, duration_var, end_var, f'interval{suffix}')


            # add to all_tasks
            all_tasks[job_id, task_id] = task_type(start=start_var,
                                                    end=end_var,
                                                    interval=interval_var,
                                                    machine=0
                                                    )



            # add conditional (alternative) machine intervals (only one of all machines is used)
            
            alt_machine_usages = []
            for alt_id,alt in enumerate(task):
                
                alternative_suffix = f'{job_id}_{task_id}_{alt_id}'
                machine_usage = model.NewBoolVar(f'presence_{alternative_suffix}')
                alt_start = model.NewIntVar(0, horizon, f'start_{alternative_suffix}')
                alt_end = model.NewIntVar(0, horizon, f'end_{alternative_suffix}')
                
                alt_interval = model.NewOptionalIntervalVar(
                    alt_start, alt.duration, alt_end, machine_usage, f'interval_{alternative_suffix}'
                )
                alt_machine_usages.append(machine_usage)

                # Link the master variables with the local ones
                model.Add(start_var == alt_start).OnlyEnforceIf(machine_usage)
                model.Add(end_var == alt_end).OnlyEnforceIf(machine_usage)
                model.Add(duration_var == alt.duration).OnlyEnforceIf(machine_usage)

                # Add local interval to the right machine
                machine_to_intervals[alt.machine].append(alt_interval)

                # Store booleans of the usages for the solution
                # print((job_id, task_id, alt_id))
                machine_usages[(job_id, task_id, alt_id)] = machine_usage

            # select exactly one machine usage per task
            model.AddExactlyOne(alt_machine_usages)#model.Add(sum(alt_machine_usages) == 1)

    # Create and add disjunctive constraints of intervals, in which a machine or tool may be used
    for machine in all_machines:
        model.AddNoOverlap(machine_to_intervals[machine])


    # Precedences inside a job.
    for job_id, job in enumerate(jobs):
        for task_id in range(len(job) - 1):
            model.Add(all_tasks[job_id, task_id + 1].start >= all_tasks[job_id, task_id].end)
    obj_var = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(obj_var, [all_tasks[job_id, len(job) - 1].end for job_id, job in enumerate(jobs)])
    model.Minimize(obj_var)

    # Solve model.
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = MAX_SEARCH_TIME_IN_SECONDS
    solution_printer = SolutionPrinter()
    status = solver.Solve(model, solution_printer)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Solve status: %s" % solver.StatusName(status))
        print("Optimal objective value: %i" % solver.ObjectiveValue())
        data=get_assigned(jobs,all_tasks,solver,machine_usages)
        view_solution(all_machines,data)
    else:
        print("Not found solution!")
        

