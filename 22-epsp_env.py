from src.core.parsers import  IParse,ExcelFileParser
from src.envs.epsp import ElectroplateJobShopEnv
from src.core.shop import JobShop 
from src.agents.mask_random import select_job
'''
solution for epsp/demo/1x(3+1).xlsx
start-0(1)       agv-4(3)     tank-2(4)                     end-3(9)
Start:J1-1|1->2
Tank1:J1-3|9->19
End:J1-5|28->29
AGV1:J1-2|2->9 J1-4|19->28
'''
# git push origin --tags
if __name__ == '__main__':
    cnt=100

    parser:IParse=ExcelFileParser()
    #ins=parser.parse('epsp/demo/1x(3+1).xlsx')
    #ins=parser.parse('epsp/demo/2x(4+1).xlsx')
    ins=parser.parse('epsp/demo/2x(6+2).xlsx')
    print(f'max_steps before extend jobs:{ins.max_steps}')
    shop=JobShop(ins)
    
    env=ElectroplateJobShopEnv(shop,min_num_job=1,max_num_job=1)
    
    
    for i in range(cnt):
       
        print(f'{"*"*6}{i+1}{"*"*6}')
        obs,info=env.reset()
        done,truncated=False,False
        if i==0:
            print(f'max_steps after extend jobs:{ins.max_steps}')
            shop.debug()
        while not done:
            #shop.debug_cranes()
            mask=info['mask']
            job_id=select_job(shop,mask)
            #print(f'mask:{mask} selected job:{job_id+1}')
            try:  
               obs,r,done,truncated,info=env.step(job_id) 
            except ValueError as e: 
                print(e) 
                done=True
            

        if r>=0:
            print(f'reward:{r}')
            env.debug()
            env.replay()
            shop.cranes[0].debug(env.makespan)
            break




        
            
