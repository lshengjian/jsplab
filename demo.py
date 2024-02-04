
#from jsplab.instances import JobShopFactory
from jsplab.utils.comm_helper import update_agv_history
import numpy as np
if __name__ == '__main__':
    #time   0   1   2   3   4   5   6   7   8   9   0   1   2   3   4
    pos   =[3,  2,  1,  0,  0,  0,  1,  2,  3,  4,  4,  4,  3,  3,  3]
    #      '←','←','←','o','o','→','→','→','→','o','o','←','o','o','o'
    #      '←','←','←','↑','↑','→','→','→','→','↓','↓','←','o','o','o'

    #['←', '←', '←', '↑', '↑', '→', '→', '→', '→', '↓', '↓', '←', 'o', 'o', 'o']
    info=update_agv_history(pos,[(3,11)])
    print(list(map(str,info)))

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


