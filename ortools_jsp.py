from jsplab import JSP_Data,Operate_type
from jsplab.utils import  load_data_list
from jsplab.solvers.ortools_jsp import slove 
from pathlib import Path
def main():
    dir = Path(__file__).parent
    ds = load_data_list(dir/'data/jsp_demo/study')
    #assert len(ds) == 1
    d: JSP_Data = ds[1]
    
    slove(d)

if __name__ == "__main__":
    main()