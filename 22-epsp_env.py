from jsplab.instances.parsers import  IParse,ParserExcel
from jsplab.envs.epsp.epsp_env import PlateJobShopEnv
import numpy as np

if __name__ == '__main__':
    cnt=10

    parser:IParse=ParserExcel()
    info=parser.parse('fjsp/demo/3x3-same.xlsx')
    env=PlateJobShopEnv({},[info.jobs]*cnt)
    
    for _ in range(cnt):
        obs,info=env.reset()
        done,timeout=False,False
        while not (done or timeout):
            obs,r,done,timeout,info=env.step(np.random.randint(0,10))
        print(env.makespan)
            
            
