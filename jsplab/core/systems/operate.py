from jsplab.utils import World,Processor
from ..components import *
import logging
logger = logging.getLogger(__name__.split('.')[-1])

class SysOperate(Processor):
    def process(self,delta_time,total_time):
        esper:World=self.world

        for ent, (m, task) in esper.get_components(Machine, WithTask):
            if esper.has_component(ent,Moveable):
                continue
            task.timer+=delta_time
            if (task.max_time<1 or task.timer>task.duration) and not esper.has_component(ent,NeedOut):
                esper.add_component(ent,NeedOut())
                logging.info(f'[{m}] requst out: {task}')

            if task.timer>task.max_time:
                esper.dispatch_event('on_fail',m,task)
                break
