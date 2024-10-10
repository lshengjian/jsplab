from jsplab.utils import World,Processor
from ..components import *


class SysBase(Processor):
    def task_enter(self,task:Task,machine_ent:int,hoist_ent:int=-1):
        esper:World=self.world
        t:Task=esper.try_component(machine_ent,Task)
        if t!=None:
            m:Machine=esper.component_for_entity(machine_ent,Machine)
            raise ValueError(f'{m} alrady had a {t}, you want put another  {t}')
        esper.remove_component(machine_ent,Scheduled)
        if hoist_ent>=0:
            esper.remove_component(hoist_ent,Task)
            #esper.dispatch_event('on_plan',machine_ent,task)#在回调函数中更新到下一个任务
            esper.add_component(machine_ent,task)
             
  