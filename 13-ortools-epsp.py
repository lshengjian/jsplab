from jsplab.instances.parsers import  IParse,ParserExcel,ParserFjspFile,InstanceInfo
from jsplab.agents.solver.epsp import solve_epsp 

if __name__ == '__main__':
    parser:IParse=ParserExcel()
    info=parser.parse('epsp/demo/2x(4+2).xlsx')
    parser.debug(info)
    solve_epsp(info)


