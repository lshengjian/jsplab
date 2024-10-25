from jsplab.conf import MultiHoistProblem

if __name__ == "__main__":
    cfg=MultiHoistProblem()
    t1,t2=cfg.get_times_ticks()
    for job_idx in t1:
        print(f'J{job_idx+1}')
        for mi in range(len(t1[job_idx])):
            print(f'  M{mi+1}:{t1[job_idx][mi]}|{t2[job_idx][mi]}')