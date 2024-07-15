from src.instances.parsers import  IParse,ParserExcel,ParserFjspFile
from src.agents.solver.fjsp import solve_fjsp 

if __name__ == '__main__':

    parser:IParse=ParserExcel()
    info=parser.parse('fjsp/demo/3x3.xlsx')
    solve_fjsp(info)
    # parser=ParserFjspFile()
    # info=parser.parse('fjsp/MK/Mk02.fjs')
    # #parser.debug(info)
    # solve_fjsp(info)

