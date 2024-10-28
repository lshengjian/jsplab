from jsplab.agents.solver import OrToolSolver
from jsplab.conf.mhp import MultiHoistProblem

def main() -> None:
    #p=MultiHoistProblem('mhp/t4j2.csv',2)
    p=MultiHoistProblem('mhp/demo.csv',3)
    solver=OrToolSolver(p)
    ticks, horizon = solver.get_max_time()
    print(horizon)
    for job_idx,ds in enumerate(ticks):
        print(f'J{job_idx+1}')
        for s in ds:
            print(f'  {s}:{ds[s]}')  
    solver.solve()


if __name__ == "__main__":
    main()
    # cfg.reset()
    # ts=cfg.get_times_ticks()
