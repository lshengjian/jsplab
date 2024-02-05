from jsplab.instances.parsers import  IParse,ParserExcel,ParserFjspFile,InstanceInfo
from jsplab.agents.solver.epsp_solver import OrToolSolver
from jsplab.utils.comm_helper import load_config
if __name__ == '__main__':
    parser:IParse=ParserExcel()
    cfg=load_config('conf/demo/or-tools-solver.yaml')
    #info=parser.parse('epsp/demo/1x(3+1).xlsx')
    info=parser.parse('epsp/demo/1x(6+2).xlsx')
    #info=parser.parse('epsp/demo/2x(4+2).xlsx')
    #info=parser.parse('epsp/demo/2x(6+2).xlsx')
    #parser.debug(info)
    solver=OrToolSolver(info,2,2)
    solver.optimize(**cfg)



