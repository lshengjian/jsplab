from jsplab.utils import World,Processor
from ..components import *
import logging
logger = logging.getLogger(__name__.split('.')[-1])

eps=1e-3
class SysDispatch(Processor):

    def select_hoist(self,tank_ent:int,tank:Machine,task:WithTask):
        esper:World=self.world
        min_dis=1e10
        hoist=None
        hoist_ent=None
        rt=False
        for ent, (m, _,_) in esper.get_components(Machine, Hoist,Moveable):
            if esper.has_component(ent,WithTask) or esper.has_component(ent,Locked):
                continue
            ds=abs(m.offset-tank.offset)
            if ds<min_dis:
                min_dis=ds
                hoist=m
                hoist_ent=ent

        if hoist!=None:
            esper.add_component(hoist_ent,MoveTarget(tank.offset,tank_ent))
            esper.add_component(hoist_ent,Locked(tank_ent))
            logger.info(f'select {m} for {task}')
            rt=True
        return rt


    def process(self,delta_time,total_time):
        esper:World=self.world
        for ent, (machine, task,_) in esper.get_components(Machine,WithTask,NeedOut):
            if (not self.select_hoist(ent,machine,task)):
                logger.info(f'machine {machine} Need Out')






                    
