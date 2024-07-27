from src.core.parsers import  IParse,ExcelFileParser
from src.envs.epsp import ElectroplateJobShopEnv
from src.core.instance import get_max_steps
from src.core.shop import JobShop 
import numpy as np
'''


'''
if __name__ == '__main__':
    cnt=1
    parser:IParse=ExcelFileParser()
    ins=parser.parse('epsp/demo/2x(3+1).xlsx')
    parser.debug(ins)
    steps=get_max_steps(ins,2,2,2)
    #actions=[(1, 0), (0, 0), (1, 3), (1, 1), (0, 3), (0, 1), (1, 3), (1, 2), (0, 3), (0, 2)]
    #ins=parser.parse('epsp/demo/2x(4+2).xlsx')
    #actions=[(1, 0), (0, 0),  (1, 1), (0, 4), (0, 2), (1, 5), (1, 3), (0, 5), (0, 3)]
    js=JobShop(ins,steps)
    env=ElectroplateJobShopEnv(js)
    obs,info=env.reset()
    done,timeout=False,False
    i=0
    while not (done or timeout):
        mask=info['mask']
        jobs=np.where(mask>0)[0]
        job_id=np.random.choice(jobs,1)[0]
        #m_id=np.random.randint(0,env.max_machines_per_task)
        #print(f'mask:{mask} select job:{job_id+1}')
        #job_id=actions[i][0]
        #print(f'select job:{job_id+1}')
        obs,r,done,timeout,info=env.step(job_id)
        i+=1

        if timeout:
            print('time out!')
        
    if not timeout: 
        env.debug()
        env.replay(0.4)
            
            
