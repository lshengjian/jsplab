from src.core.parsers import  IParse,ExcelFileParser,StandardFjspFileParser
from src.agents.solver.fjsp import solve_fjsp 

if __name__ == '__main__':

    parser:IParse=ExcelFileParser()
    info=parser.parse('fjsp/demo/3x3.xlsx')
    solve_fjsp(info)
    parser=StandardFjspFileParser()
    info=parser.parse('fjsp/MK/Mk01.fjs')
    #parser.debug(info)
    solve_fjsp(info)

