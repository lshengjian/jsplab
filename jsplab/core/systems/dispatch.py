from jsplab.utils import World,Processor
from jsplab.conf import G
from ..components import*
from ...conf.shop import get_offset
import logging
logger = logging.getLogger(__name__.split('.')[-1])

eps=1e-3
class SysDispatch(Processor):

    def select_hoist(self,machine_ent:int,machine:Machine,task:Task):
        esper:World=self.world
        min_dis=1e10
        hoist_ent=None
        target=get_offset(machine.init_slot)
        data= esper.try_component(machine_ent,Movable)
        if data!=None:
            target=data.offset
        for ent, (m, _,_) in esper.get_components(Movable,Hoist,Free):
            ds=abs(m.offset-target)
            if ds<min_dis:
                min_dis=ds
                hoist_ent=ent

        if hoist_ent!=None:
            esper.add_component(hoist_ent,MoveTarget(target,machine_ent))
            esper.remove_component(hoist_ent,Free)
            m:Machine= esper.try_component(hoist_ent,Machine)
            logger.info(f'select {m} for {task}')
        return hoist_ent


    def process(self,delta_time,total_time):
        esper:World=self.world
        for ent, (machine, task,_) in esper.get_components(Machine,Task,RequestPickup):
            print(machine)
            h_id=self.select_hoist(ent,machine,task)
            if (h_id!=None):
                p=esper.remove_component(ent,RequestPickup) 
                # print(p)
                # p=esper.try_component(ent,RequestPickup)
                # print(p)

                esper.add_component(ent,Scheduled(h_id))
            else:
                logger.info(f'not hoist! for {machine}')
            
               





                    
