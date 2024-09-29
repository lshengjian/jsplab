from jsplab.utils import World,Processor
from ..components import Machine,Moveable,MoveTarget,Pickup,Dropdown,CanUpDown,Task
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
                    esper.dispatch_event('on_arrived',ent,target)
                    esper.remove_component(ent,MoveTarget)
                    
                    
class SysPickup(Processor):
    def process(self,delta_time,total_time):
        esper:World=self.world
        for ent, (m, p,data) in esper.get_components(Machine,Pickup,CanUpDown):
            p.timer+=delta_time
            if p.timer>data.up_time:
                esper.remove_component(ent,Pickup)
                task:Task=esper.component_for_entity(ent,Task)
                #task.op_machine_offsets=[]
                esper.add_component(ent,MoveTarget(6))