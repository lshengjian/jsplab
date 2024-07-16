from src.core.parsers import  IParse,StandardJspFileParser,ExcelFileParser
from src.agents.solver.jsp import solve_jsp 

if __name__ == '__main__':
    parser:IParse=StandardJspFileParser()
    info=parser.parse('jsp/demo/3x3')
    solve_jsp(info)
    parser=ExcelFileParser()
    info=parser.parse('jsp/demo/3x3.xlsx')
    solve_jsp(info)

