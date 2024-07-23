from collections import defaultdict,namedtuple
from typing import Dict,List
from ortools.sat.python import cp_model

MAX_SEARCH_TIME_IN_SECONDS=20

task_type = namedtuple("task_type", "start end interval machine")
assigned_task_type = namedtuple(
    "assigned_task_type", "start job index duration machine"
)
class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__solution_count = 0

    def on_solution_callback(self):
        """Called at each new solution."""
        print(
            "Solution %i, time = %f s, objective = %i"
            % (self.__solution_count, self.WallTime(), self.ObjectiveValue())
        )
        self.__solution_count += 1

def get_assigned(jobs,all_tasks,solver,presences):
    assigned_jobs = defaultdict(list)
    for job_id, job in enumerate(jobs):
        for task_id, task in enumerate(job):
            task_info=all_tasks[(job_id, task_id)]
            machine=-1
            for alt_id,alt in enumerate(task):
                if solver.Value(presences[job_id, task_id,alt_id]):
                    machine = alt.machine
                    break
            
            task_start=solver.Value(task_info.start)
            task_end=solver.Value(task_info.end)

            
            assigned_jobs[machine].append(
                assigned_task_type(
                    start=task_start,
                    job=job_id,
                    index=task_id,
                    duration=task_end-task_start,
                    machine=machine)
            )
    return assigned_jobs

def view_solution(offsets:Dict[int,int],assigned_jobs:Dict[int,assigned_task_type]):
    print('Solution:')
    output = ''
    
    #ms.reverse()
    for machine,x in enumerate(offsets):
        # Sort by starting time.
        assigned_jobs[machine].sort()
        sol_line_tasks = f'M{str(machine+1)}[{x}]: '
        sol_line = ' '*7
        for t in assigned_jobs[machine]:
            name = f'{t.job+1}-{t.index+1}'
            # Add spaces to output to align columns.
            sol_line_tasks += f'{name:<8}' 
            start = t.start
            duration = t.duration
            sol_tmp = f'[{start},{start + duration}]'
             # Add spaces to output to align columns.
            sol_line += f'{sol_tmp:<8}' 

        sol_line += '\n'
        sol_line_tasks += '\n'
        output += sol_line_tasks
        output += sol_line
   
    print(output)
