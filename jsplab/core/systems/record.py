from jsplab.utils import World,Processor
from ..components import Machine, Trajectory
eps=1e-3
class SysRecord(Processor):
    def process(self,delta_time,total_time):
        esper:World=self.world
        for ent, (m, traj) in esper.get_components(Machine, Trajectory):
            if len(traj.history)<1:
                traj.history.append((0,m.init_offset))
            t=round(total_time)
            dx=abs(traj.history[-1][1]-m.offset)
            if dx<=eps:
                 continue
            last_time=traj.history[-1][0]
            if abs(t-last_time)>eps:
                traj.history.append((t,m.offset))
