from jsplab.instances.parsers import  IParse,ParserStandardJspFile,ParserExcel
from jsplab.agents.solver.jsp import solve_jsp 

if __name__ == '__main__':
    parser:IParse=ParserStandardJspFile()
    info=parser.parse('jsp/demo/3x3')
    solve_jsp(info)
    parser=ParserExcel()
    info=parser.parse('jsp/demo/3x3.xlsx')
    solve_jsp(info)

