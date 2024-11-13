from jsplab.core import *
from jsplab.conf.mhp import ConfigMHP
from jsplab.siaf import LSO,PSO
import numpy as np
from numpy.typing import NDArray
def extend_numpy_list(data:List[NDArray])->List[NDArray]:
    '''
    对列表中numpy数据进行填充,使得各行的长度相同
    '''
    # 找到数据最多的行 
    dim=len(data[0].shape)
    num_cols=map(lambda d:len(d[0]),data) if dim>1 else map(lambda d:len(d),data) 
    max_num =max(num_cols) 
    rt=[]
    for ds in data:
        if dim>1:
            expanded_data = np.pad(ds, ((0, 0), (0,max_num-len(ds[0]))), 'edge') 
        else:
            expanded_data = np.pad(ds, (0,max_num-len(ds)), 'edge') 
        rt.append(expanded_data) 
    return rt

def main():
    #cfg=ConfigMHP('mhp/t4j2.csv',2)
    cfg=ConfigMHP('mhp/demo.csv',2)
    p=MultiHoistProblem(cfg)
    #opt1=PSO(30)
    opt=LSO(30)

    opt.reset(p)
    cost,x=opt.run(1)
    print(cost)


    #p.show(best_x)



if __name__ == "__main__":
    main()
