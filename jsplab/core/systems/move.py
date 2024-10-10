from jsplab.utils import World,Processor
from jsplab.conf import G
from ..components import*
from ...conf.shop import get_offset

import logging
logger = logging.getLogger(__name__.split('.')[-1])

class SysMove(Processor):
    def process(self,delta_time,total_time):
        esper:World=self.world
        self.move_transfer(delta_time, esper)
        self.move_hoist(delta_time, esper)

    def move_hoist(self, delta_time, esper):
        for ent, (machine, move,target,_) in esper.get_components(Machine,Movable,MoveTarget,Hoist):
            max_offset=get_offset(move.max_slot)
            min_offset=get_offset(move.min_slot)
            #print(move,target)
            assert min_offset<=target.to_offset<=max_offset
            ds= target.to_offset-move.offset
            ads=abs(ds)
            if ads>G.EPS:
                dir=ds/ads
                move.offset+=delta_time*move.speed*dir
                finished=False
                ds2= target.to_offset-move.offset
                if ds*ds2<=0:
                    move.offset=target.to_offset
                    finished=True
                logger.debug(f'{machine}|{move.offset}')
                if finished :
                    esper.dispatch_event('on_arrived',ent,machine)
                    esper.remove_component(ent,MoveTarget) 
                    task:Task=esper.try_component(ent,Task)
                    if (task!=None):
                       esper.add_component(ent,Dropdown(target.machine_ent))
                    elif (esper.has_component(target.machine_ent,Task)):
                        esper.remove_component(target.machine_ent,Scheduled)
                        task:Task=esper.component_for_entity(target.machine_ent,Task)
                        esper.remove_component(target.machine_ent,Task)
                        
                        esper.dispatch_event('on_picked',ent,task)#在回调函数中更新到下一个任务
                        esper.add_component(ent,task)
                        esper.add_component(ent,Pickup())
                        logger.info(f'pickup {task}')

    def move_transfer(self, delta_time, esper):
        for ent, (machine, move,_) in esper.get_components(Machine,Movable,Transfer):
            task:Task=esper.try_component(ent,Task)
            max_offset=get_offset(move.max_slot)
            min_offset=get_offset(move.min_slot)
            

            ds= min_offset-move.offset if task is None else  max_offset-move.offset
            ads=abs(ds)
            if ads>G.EPS:
                dir=ds/ads
                move.offset+=delta_time*move.speed*dir
                finished=False
                if move.offset>=max_offset:
                    move.offset=max_offset
                    finished=True
                if move.offset<=min_offset:
                    move.offset=min_offset
                    finished=True
                logger.debug(f'{machine}|{move.offset}')
                if finished :
                    esper.dispatch_event('on_arrived',ent,machine)
                    if abs(move.offset- max_offset)<G.EPS:
                        esper.add_component(ent,RequestPickup())
                    if abs(move.offset- min_offset)<G.EPS:
                        esper.add_component(ent,Free())

                   
                         
                    
                    
class SysPickup(Processor):
    def process(self,delta_time,total_time):
        esper:World=self.world
        for ent, (m, p,h) in esper.get_components(Machine,Pickup,Hoist):
            p.timer+=delta_time
            h.offset_y+=0.5 #todo
            logger.debug(f'{m}|y:{h.offset_y}')

            if p.timer>h.up_time:
                esper.remove_component(ent,Pickup)
                h.offset_y=2
                #todo 
                esper.add_component(ent,MoveTarget(18,4))


class SysDropdown(Processor):
    def process(self,delta_time,total_time):
        esper:World=self.world
        for ent, (p,h,m) in esper.get_components(Dropdown,Hoist,Machine):
            p.timer+=delta_time
            h.offset_y-=0.5
            logger.debug(f'{m}|y:{h.offset_y}')
            if p.timer>h.down_time:
                esper.remove_component(ent,Dropdown)
                h.offset_y=0
                if self.world.has_component(ent,Task):
                    task=self.world.component_for_entity(ent,Task)
                    self.world.remove_component(ent,Task)
                    self.world.add_component(p.machine_ent,task)
                    self.world.remove_component(p.machine_ent,Free)

                    # self.world.add_component(move_ent,task)
                