
from src.core import *
 
def test_crane():
    paser:IParse=ExcelFileParser()
    ins=paser.parse('epsp/demo/1x(3+1).xlsx')
    shop=JobShop(ins,30,2)
    

    start:Tank = shop.machines[0]
    tank:Tank = shop.machines[1]
    end:Tank = shop.machines[2]
    crane:OverHeadCrane=shop.machines[3]
    
    j1=shop.jobs[0]

    assert j1.cur_task.index==0
    j1.assign(crane,start,tank)

    assert j1.cur_task.index==2

    t=j1.tasks[0]
    m=shop.machines[t.selected_machine]
    print(t,m)
    crane.debug()
    assert m.name=='Start' and t.runtime==1 and t.time_started==1 and t.time_finished==2
     
    t=j1.tasks[1]
    m=shop.machines[t.selected_machine]
    print(t,m)
    assert m.name=='AGV1' and t.runtime==7 and t.time_started==2 and t.time_finished==9
    # crane.debug()
    # j1.assign(crane,tank,end)
    # t=j1.tasks[2]
    # m=shop.machines[t.selected_machine]
    # print(t,m)
    # t=j1.tasks[3]
    # m=shop.machines[t.selected_machine]
    # print(t,m)
    # crane.debug()
    # j1.assign(None,end,None)
    # t=j1.tasks[4]
    # m=shop.machines[t.selected_machine]
    # print(t,m)


if __name__ == '__main__':
    #test_extend()
    test_crane()