from jsplab.instances.parsers import  IParse,ParserExcel
from jsplab.envs.fjsp.fjsp_env import FlexJobShopEnv
from jsplab.agents.solver.fjsp import solve_fjsp 
import numpy as np

if __name__ == '__main__':
    cnt=3

    parser:IParse=ParserExcel()
    info=parser.parse('fjsp/demo/3x3-same.xlsx')
    #info=parser.parse('fjsp/demo/3x3.xlsx')
    steps,actions=solve_fjsp(info)
    print("or-tools:",steps)
    print(actions)#[2, 1, 0, 2, 1, 0, 2, 1, 0]
    env=FlexJobShopEnv({},[info.jobs]*cnt)
    
    for i in range(cnt):
        idx=0
        obs,info=env.reset()
        print(f'===instance {i+1}====')
        done=False
        while not done:
            mask=info['mask']

            if i==0:
                data=actions[idx]
                job=data//100
                machine=data%100
            else:
                jobs=np.where(mask>0)[0]
                job=np.random.choice(jobs,1)[0]
                machine=np.random.randint(0,env.num_machines)
                

                       
            obs,r,done,timeout,info=env.step(env.num_machines*job+machine)
            idx+=1
            
            if timeout:
                print('time out')
                break
            
            
