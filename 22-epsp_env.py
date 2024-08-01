from src.core.parsers import  IParse,ExcelFileParser
from src.envs.epsp import ElectroplateJobShopEnv
from src.core.instance import get_max_steps
from src.core.shop import JobShop 
import numpy as np
'''
start-0(1)       agv-4(3)     tank-2(4)                     end-3(9)
Start:J1-1|1->2
Tank1:J1-3|9->19
End:J1-5|28->29
AGV1:J1-2|2->9 J1-4|19->28
'''
if __name__ == '__main__':

    parser:IParse=ExcelFileParser()
    ins=parser.parse('epsp/demo/2x(3+1).xlsx')
    parser.debug(ins)
    shop=JobShop(ins)
    
    
    env=ElectroplateJobShopEnv(shop)
    obs,info=env.reset()
    done,timeout=False,False


    while not (done or timeout):
        mask=info['mask']
        jobs=np.where(mask>0)[0]
        job_id=np.random.choice(jobs,1)[0]
        print(f'mask:{mask} selected job:{job_id+1}')

        obs,r,done,timeout,info=env.step(job_id)


    env.debug()
    env.replay(0.4)
    shop.cranes[0].debug()
        
            
