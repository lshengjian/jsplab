from jsplab.envs.environment_loader import EnvironmentLoader
from jsplab.instances.parsers import  IParse,ParserExcel,ParserFjspFile
from jsplab.agents.solver.fjsp import solve_fjsp 
from jsplab.agents.test import run_episode
if __name__ == '__main__':
    parser:IParse=ParserExcel()
    info=parser.parse('fjsp/demo/3x3.xlsx')
    steps,actions=solve_fjsp(info)
    print("or-tools:",steps)
    print(actions)
    instance_list=[info.jobs]
    # compute_initial_instance_solution(instance_list,{})
    # set_deadlines_to_max_deadline_per_job(instance_list)

    # compute individual hash for each instance
    # JobShopFactory.compute_and_set_hashes(instance_list)
    env,name=EnvironmentLoader.load({},data=instance_list)
    actions=[2, 0, 1, 2, 1, 0, 1, 2, 0]
    for a in actions:
        env.step(a)
        print(env.get_makespan())

    TEST_HEURISTICS = ['MTR','rand','SPT', 'EDD',   'LTR']#'MTR' is best
    for t in TEST_HEURISTICS:
        env.reset()
        run_episode(env,None,t)
        print(t,env.get_makespan())
        print(env.action_history)