from src.envs.old.environment_loader import EnvironmentLoader
from src.core.parsers import  IParse,ParserExcel,ParserFjspFile
from src.agents.solver.fjsp import solve_fjsp 
from src.envs.epsp_env import PlateJobShopEnv
from src.agents.test import run_episode
if __name__ == '__main__':
    parser:IParse=ParserExcel()
    info=parser.parse('fjsp/demo/3x3-same.xlsx')
    steps,actions=solve_fjsp(info)
    print("or-tools:",steps)
    print(actions)
    instance_list=[info.tasks]
    env=PlateJobShopEnv({},[info.tasks]*1)


    TEST_HEURISTICS = ['rand','MTR','SPT', 'EDD',   'LTR']#'MTR' is best
    for t in TEST_HEURISTICS:
        env.reset()
        run_episode(env,None,t)
        print(t,env.get_makespan())
        #print(env.action_history)