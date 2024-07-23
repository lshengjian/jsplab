from src.core.parsers import  IParse,ExcelFileParser
from src.envs.epsp import ElectroplateJobShopEnv
from src.utils.render import replay
from src.core.crane_state import make_crane_states
import numpy as np

if __name__ == '__main__':
    cnt=1

    parser:IParse=ExcelFileParser()
    ins=parser.parse('epsp/demo/2x(3+1).xlsx')
    #parser.debug(info)
    

    env=ElectroplateJobShopEnv({'machine_offsets':ins.machine_offsets,
                                'first_crane_index':ins.first_crane_index,
                                'machine_names':ins.machine_names},
                                [ins.tasks]*cnt)
    

    obs,info=env.reset()
    done,timeout=False,False
    while not (done or timeout):
        mask=info['mask']
        jobs=np.where(mask>0)[0]
        if len(jobs)<1:
            break
        job_id=np.random.choice(jobs,1)[0]
        #m_id=np.random.randint(0,env.max_machines_per_task)
        #print(f'mask:{mask} select job:{job_id+1}')
        obs,r,done,timeout,info=env.step(job_id)
        
    #print(env.makespan)
    for m,ts in env.machine_tasks.items():
        print(f'M{m+1}:',end='')
        for task in ts:
            print(f'{task}',end=' ')
        print()

    data=[]
    for m,agv in env.cranes.items():
        tasks=env.machine_tasks[m]
        moves=[]
        for task in tasks:
            moves.append((task.time_started,task.time_finished))
        flags=make_crane_states(agv.pos,moves,2,2)
        flags=list(map(str,flags))
        data.append((agv.pos,flags))
    x1=min(ins.machine_offsets)
    x2=max(ins.machine_offsets)
    start=ins.first_crane_index
    replay(x1,x2,start,env.makespan,0.4,ins.machine_offsets,data)
        
            
