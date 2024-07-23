
from src.core import *
import numpy as np
def demo():
    paser:IParse=ExcelFileParser()
    info=paser.parse('jsp/demo/3x3.xlsx')
    paser.debug(info) #pytest -s
    assert '3x3'==info.name
    data=info.tasks
    assert 8==len(data) 
    assert 'J1-1|3'==str(data[0])
    assert 'J1-1|3,[(1,3)]'==data[0].info()
    assert 'J1-2|2,[(2,2)]'==data[1].info()
    assert 1==info.max_machines_per_task
    # wd=World('test03')
    # wd.reset()
    #wd.add_jobs(['A']*2+['B']*3)
    # assert len(wd.group_cranes)==1
    # x1,x2=wd.group_limits[1]
    # assert x1==1 and x2==9
    # wd.add_jobs(['A']*2)
    # assert len(wd.products)==2
    # assert wd.starts[0].carrying is None
    # assert wd.starts[1].carrying is None

    # assert len(wd.pos_slots)==7
    # assert len(wd.product_procs['A'])==3
    # wd.pprint()
    # rd=Renderer(wd)
    # for _ in range(100):
    #     wd.update()
    #     rd.render('human')
    
if __name__ == '__main__':
    demo()

 