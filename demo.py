
from jsplab.instances import JobShopFactory
from jsplab.instances.parsers import  IParse,ParserExcel,ParserStandardJspFile,ParserFjspFile
from jsplab.instances.maker import *
from jsplab.agents.solver.jsp import solve_jsp 
from jsplab.core import convert2jsp_data
from jsplab.instances import InstanceInfo
import numpy as np
if __name__ == '__main__':
    info=InstanceInfo('test',first_agv_index=3)
    print(info)
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


