from dataclasses import dataclass as component
import time
from jsplab.utils import World,Processor

##################################
#  Define some Components:
##################################
@component
class RecordTime:
    total_free: float = 0.0
    total_working: float = 0.0

@component
class RecordPos:
    last_time: float = 0.0
    offset: float = 0.0
    history=[]

@component
class Machine:
    index:int=0
    init_offset:float=0.0
    offset:float=0.0 
    is_free: bool = True


@component
class Trans:
    min_offset:float=0 
    max_offset:float=0
    speed:float=1.0



@component
class Go:
    pass
@component
class Back:
    pass

# @component
# class Hoist(Trans):
#     pickup_time:float=6.0
#     dropdown_time:float=6.0

# @component
# class Command:
#     from_offset:float=0.0 
#     to_offset:float=0.0
#     is_pause:bool=False
################################
#  Define some Processors:
################################
class RecordPosSys(Processor):
    def process(self,dt,t):
        esper:World=self.world
        for ent, (m, r) in esper.get_components(Machine, RecordPos):
            if len(r.history)<1:
                r.history.append((0,m.init_offset))
                r.last_time=0
            t=round(t)
            if abs(t-r.last_time)>0.001:
                r.last_time=t
                dx=abs(r.history[-1][1]-m.offset)
                if dx>0.01:
                    r.history.append((t,m.offset))


# class TimeSys(Processor):
#     def process(self,dt,t):
#         esper:World=self.world
#         for ent, (m, r) in esper.get_components(Machine, RecordTime):
#             if m.is_free:
#                 r.total_free+=dt
#             else:
#                 r.total_working+=dt
class TransSys(Processor):
    def process(self,dt,tt):
        esper:World=self.world
        for ent, (m,t, _) in esper.get_components(Machine,Trans, Go):
            if m.offset<t.max_offset:
                m.offset+=dt*t.speed
                if m.offset>=t.max_offset:
                    m.offset=t.max_offset
                    esper.remove_component(ent,Go)
                    esper.dispatch_event('on_tran_arrived',esper,ent,tt)
        for ent, (m,t, _) in esper.get_components(Machine,Trans, Back):
            if m.offset>t.min_offset:
                m.offset-=dt*t.speed
                if m.offset<=t.min_offset:
                    m.offset=t.min_offset
                    esper.remove_component(ent,Back)
                    esper.dispatch_event('on_tran_back',esper,ent,tt)

def tran_arrived(esper,ent,t):
    print(f"tran_arrived:{t:.1f}")
def tran_back(esper,ent,t):
    print(f"tran_back:{t:.1f}")
def dispaly(esper,ent):
    rt:RecordPos=esper.component_for_entity(ent, RecordPos)
    print(rt.history)

'''
0 1 2 3 4 5 6 7 8 9 0 T
  S     H           1
                    2
3 2 1 0 9 8 7 6 5 4 3  

'''

def test_ecs():
    esper=World()
    esper.set_handler('on_tran_arrived', tran_arrived)
    esper.set_handler('on_tran_back', tran_back)

    esper.add_processor(RecordPosSys())
    esper.add_processor(TransSys(),priority=1)


    e1=esper.create_entity(Machine(3,10,10),Trans(10,13),RecordPos(),Go())
    t=0
    dt=1
    for i in range(20):
        t+=dt
        if i==5:
            esper.add_component(e1,Back())
        esper.process(dt,t)
    esper.set_handler('on_end', dispaly)
    esper.dispatch_event('on_end',esper,e1)
    rp:RecordPos=esper.component_for_entity(e1, RecordPos)
    assert 7==len(rp.history)
    assert (0, 10)==rp.history[0]
    assert (8, 10)==rp.history[-1]
