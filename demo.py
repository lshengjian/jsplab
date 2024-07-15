
from src.agents.solver.epsp import solve_epsp
from src.instances.parsers import *
from src.utils.common import load_config
if __name__ == '__main__':
    cfg=load_config('conf/demo/or-tools-solver.yaml')
    print(cfg)
    #parser:IParse=ParserExcel()
    #info=parser.parse('epsp/demo/1x(3+1).xlsx')
    #parser.debug(info)
    #solve_epsp(info)

    # parser:IParse=ParserStandardJspFile()
    # name,data=parser.parse('jsp/demo1/3x3')
    # data=convert2jsp_data(data)
    # solve_jsp(data)

    # instance_list=[data]

    # main('fjssp/config_job3_task4_tools0.pkl','makespan')
    #instance_list=JobShopFactory.generate_instances()



    # instance_list=compute_initial_instance_solution(instance_list,{})
    # JobShopFactory.set_deadlines_to_max_deadline_per_job(instance_list, 2)
    # JobShopFactory.compute_and_set_hashes(instance_list)
    # or_tool_solver = OrToolSolver()
    # for data in instance_list:
    #     assigned_jobs, objective_value = or_tool_solver.optimize(data, objective='makespan')
    #     print(objective_value)


