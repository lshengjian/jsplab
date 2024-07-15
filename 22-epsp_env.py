from src.instances.parsers import  IParse,ParserExcel
from src.envs.epsp_env import PlateJobShopEnv
import numpy as np

if __name__ == '__main__':
    cnt=1

    parser:IParse=ParserExcel()
    info=parser.parse('epsp/demo/2x(4+2).xlsx')
    env=PlateJobShopEnv({},[info.jobs]*cnt)
    
    for _ in range(cnt):
        obs,info=env.reset()
        done,timeout=False,False
        while not (done or timeout):
            obs,r,done,timeout,info=env.step(np.random.randint(0,10))
        print(env.makespan)
            
            
