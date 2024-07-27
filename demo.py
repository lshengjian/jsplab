from src.core import  *
phaser:IParse=ExcelFileParser()
  
ins=phaser.parse('epsp/demo/2x(3+1).xlsx')
shop=JobShop(ins,50,2)
assert 2==len(shop.jobs)
assert 4==len(shop.machines)

start:Tank = shop.machines[0]
tank:Tank = shop.machines[1]
end:Tank = shop.machines[2]
crane:OverHeadCrane=shop.machines[3]
crane.debug()
j1=shop.jobs[0]
print(j1.cur_task)
j1.assign(crane,start,tank)
print(j1.cur_task)
t=j1.tasks[0]
m=shop.machines[t.selected_machine]
print(t,m)
t=j1.tasks[1]
m=shop.machines[t.selected_machine]
print(t,m)
crane.debug()
j1.assign(crane,tank,end)
t=j1.tasks[2]
m=shop.machines[t.selected_machine]
print(t,m)
t=j1.tasks[3]
m=shop.machines[t.selected_machine]
print(t,m)
crane.debug()
j1.assign(None,end,None)
t=j1.tasks[4]
m=shop.machines[t.selected_machine]
print(t,m)

