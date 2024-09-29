from jsplab.utils import World,Processor
from ..components import Machine,Moveable,MoveTarget,CanUpDown,Job,Task
eps=1e-3
class SysDispatch(Processor):
    def select_hoist(self,tank:Machine,job:Job,task:Task):
        esper:World=self.world
        min_dis=1e10
        hoist=None
        hoist_ent=None
        for ent, (h, updown,data) in esper.get_components(Machine, CanUpDown,Moveable):
            if not h.is_free:
                continue
            # flag=False
            # offset=-1
            # for d in task.op_machine_offsets:
            #     if abs(d-m.offset)<eps:
            #         flag=True
            #         offset=d
            #         break
            # if not flag:
            #     continue

            ds=abs(h.offset-tank.offset)
            if ds<min_dis:
                min_dis=ds
                hoist=h
                hoist_ent=ent

            if hoist!=None:
                esper.add_component(hoist_ent,MoveTarget(tank.offset))
                task.selected_machine_id=tank.id

    def process(self,delta_time,total_time):
        esper:World=self.world
        for ent, (machine, job,task) in esper.get_components(Machine,Job,Task):
            if task.selected_machine_id<0:
                self.select_hoist(machine,job,task)




                    
