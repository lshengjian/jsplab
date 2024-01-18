from jsplab import JSP_Data, OperateType
from jsplab.instances import load_data_list
from jsplab.solvers.ortools_jsp import slove
from pathlib import Path


def main():
    dir = Path(__file__).parent
    ds = load_data_list(dir/'data/jsp_demo/study')

    slove(ds[0])


if __name__ == "__main__":
    main()
