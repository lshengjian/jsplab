from jsplab.utils import World,Processor
from ..components import *
import logging
logger = logging.getLogger(__name__.split('.')[-1])

class SysOperate(Processor):
    def process(self,delta_time,total_time):
        esper:World=self.world

        for ent, (m,tank, task) in esper.get_components(Machine, Tank,Task):
            
            task.timer+=delta_time
            if task.duration>0 and task.timer>task.duration*1.2:
                esper.dispatch_event('on_fail',ent)
                break
            if (task.duration<1 or task.timer>task.duration):
                if esper.has_component(ent,RequestPickup)==False:
                    esper.add_component(ent,RequestPickup())
                    logging.info(f'{m} Request Pickup: {task}')


