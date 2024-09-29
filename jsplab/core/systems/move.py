from jsplab.utils import World,Processor
from ..components import Machine,Moveable,MoveTarget
eps=1e-3
class SysMove(Processor):
    def process(self,delta_time,total_time):
        esper:World=self.world
        for ent, (m, target,data) in esper.get_components(Machine, MoveTarget,Moveable):
            ds=abs(m.offset-target.to_offset)
            if ds>eps:
                dir=(target.to_offset-m.offset)/ds
                m.offset+=delta_time*data.speed*dir
                over=False
                if m.offset>=data.max_offset:
                    m.offset=data.max_offset
                    over=True
                if m.offset<=data.min_offset:
                    m.offset=data.min_offset
                    over=True
                if over:
                    esper.dispatch_event('on_arrived',ent,target)
                    esper.remove_component(ent,MoveTarget)
                    
