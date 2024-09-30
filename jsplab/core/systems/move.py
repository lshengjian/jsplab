from jsplab.utils import World,Processor
from ..components import*
import logging
logger = logging.getLogger(__name__.split('.')[-1])
eps=1e-3
class SysMove(Processor):
    def process(self,delta_time,total_time):
        esper:World=self.world
        for ent, (m, target,data) in esper.get_components(Machine, MoveTarget,Moveable):
            ds=abs(m.offset-target.to_offset)
            if ds>eps:
                dir=(target.to_offset-m.offset)/ds
                m.offset+=delta_time*data.speed*dir
                finished=False
                if m.offset>=data.max_offset:
                    m.offset=data.max_offset
                    finished=True
                if m.offset<=data.min_offset:
                    m.offset=data.min_offset
                    finished=True
                if finished:
                    esper.remove_component(ent,MoveTarget)
                    esper.dispatch_event('on_arrived',ent,target)
                    
                    
                    
class SysPickup(Processor):
    def process(self,delta_time,total_time):
        esper:World=self.world
        for ent, (m, p,data) in esper.get_components(Machine,Pickup,Hoist):
            p.timer+=delta_time
            if p.timer>data.up_time:
                esper.remove_component(ent,Pickup)
                
                data.offset_y=2
                #task:Task=esper.component_for_entity(ent,Task)
                #task.op_machine_offsets=[]
                #todo 
                esper.add_component(ent,MoveTarget(6))
                lk=esper.component_for_entity(ent,Locked)
                lk.machie_entity=21

class SysDropdown(Processor):
    def process(self,delta_time,total_time):
        esper:World=self.world
        for ent, (m, p,data) in esper.get_components(Machine,Dropdown,Hoist):
            p.timer+=delta_time
            if p.timer>data.down_time:
                esper.remove_component(ent,Dropdown)
                data.offset_y=0
                if self.world.has_component(ent,WithTask):
                    task=self.world.component_for_entity(ent,WithTask)
                    self.world.remove_component(ent,WithTask)
                    # self.world.add_component(move_ent,job)
                    # self.world.add_component(move_ent,task)
                