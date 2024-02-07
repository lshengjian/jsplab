from jsplab.envs.environment_loader import EnvironmentLoader
from jsplab.instances.parsers import  IParse,ParserExcel,ParserFjspFile
from jsplab.agents.solver.fjsp import solve_fjsp 
from jsplab.envs.epsp.epsp_env import PlateJobShopEnv
from jsplab.agents.test import run_episode
if __name__ == '__main__':
    parser:IParse=ParserExcel()
    info=parser.parse('fjsp/demo/3x3-same.xlsx')
    steps,actions=solve_fjsp(info)
    print("or-tools:",steps)
    print(actions)
    instance_list=[info.jobs]
    env=PlateJobShopEnv({},[info.jobs]*1)


    TEST_HEURISTICS = ['rand','MTR','SPT', 'EDD',   'LTR']#'MTR' is best
    for t in TEST_HEURISTICS:
        env.reset()
        run_episode(env,None,t)
        print(t,env.get_makespan())
        #print(env.action_history)