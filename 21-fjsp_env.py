from jsplab.instances.parsers import  IParse,ParserExcel,ParserFjspFile
from jsplab.envs.fjsp.fjsp_env import FlexJobShopEnv
from jsplab.agents.solver.fjsp import solve_fjsp 
import numpy as np

if __name__ == '__main__':
    cnt=2

    #parser:IParse=ParserExcel()
    #info=parser.parse('fjsp/demo/3x3.xlsx')

    #
    parser:IParse=ParserFjspFile()
    info=parser.parse('fjsp/MK/Mk01.fjs')
    steps,actions=solve_fjsp(info)
    print("or-tools:",steps)
    print(actions)

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
                selected_task_id, selected_task = env.get_selected_task(job)
                machine=env.choose_machine(selected_task)#np.random.randint(0,env.num_machines)
                       
            obs,r,done,timeout,info=env.step(env.num_machines*job+machine)
            idx+=1
            
            if timeout:
                print('time out')
                break
            
            
