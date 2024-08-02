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
    cnt=3

    parser:IParse=ExcelFileParser()
    #ins=parser.parse('epsp/demo/1x(3+1).xlsx')
    #ins=parser.parse('epsp/demo/2x(3+1).xlsx')
    ins=parser.parse('epsp/demo/2x(4+1).xlsx')
    #ins=parser.parse('epsp/demo/2x(6+2).xlsx')
    
    shop=JobShop(ins)
    env=ElectroplateJobShopEnv(shop,1,3)
    
    print(f'max_steps:{env.shop.instance.max_steps}')
    for i in range(cnt):
       
        print(f'{"*"*6}{i+1}{"*"*6}')
        obs,info=env.reset()
        done,timeout=False,False
        if i==0:
            shop.debug()
        while not done:
            mask=info['mask']
            jobs=np.where(mask>0)[0]
            job_id=np.random.choice(jobs,1)[0]
            print(f'mask:{mask} selected job:{job_id+1}')
            try:  
               obs,r,done,timeout,info=env.step(job_id) 
            except ValueError as e: 
                print(e) 
                done=True
            

        if r>=0:
            env.debug()
            env.replay()
            shop.cranes[0].debug(env.get_makespan())
            break




        
            
