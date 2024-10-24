
from jsplab.core import *
from jsplab.conf import MultiHoistProblem,G
from jsplab.cbd import GameObject,EventManager
from typing import List,Union
import logging,math,random
from pyglet.shapes import Circle,BorderedRectangle
logger = logging.getLogger(__name__.split('.')[-1])

class JobShop:
    def __init__(self,p:MultiHoistProblem,num_hoists=2):
        self.problem:MultiHoistProblem=p
        self.num_hoists=num_hoists
        self.num_jobs=len(p.procs)
        self.hoists:List[Hoist]=[]
        self.tanks:List[Tank]=[]
        self.center=EventManager()
        self.center.subscribe('on_scheduling',self.on_scheduling)
        self.center.subscribe('on_timeout',self.on_timeout)
        self.center.subscribe('on_hoist_pickup',self.on_hoist_pickup)
        self.center.subscribe('on_hoist_drop',self.on_hoist_drop)
        self.reset()
    
    def select_hoists_by_offset(self,offset)->List[int]:
        safe_dis=G.HOIST_SAFE_DISTANCE
        n=self.num_hoists
        if offset==self.problem.min_offset:
            return [0]
        if offset==self.problem.max_offset:
            return [n-1]
    
        hs=set(range(n))
        
        dx1=abs(offset-self.problem.min_offset)
        n1=dx1//safe_dis
        hs=hs-set(range(n1,n)) #左边的安全要求
        dx2=abs(self.problem.max_offset-offset)
        n2=n-dx2//safe_dis
        hs=hs-set(range(0,n2))
        return list(hs)
        # for i,h in enumerate(self.hoists):
        #     if  i*safe_dis
    def make_jobs(self):
        cfg:MultiHoistProblem=self.problem
        #num_hoists=self.num_hoists
        offsets=cfg.tank_offsets
        min_offset,max_offset=min(offsets),max(offsets)
        rt=[]
        for job_index,proc in enumerate(cfg.procs):
            tasks=[]
            for step in proc:
                task=Task(step)
                task.can_move_hoists=self.select_hoists_by_offset(step.offset)
                #print(task,task.can_move_hoists)
                # if step.offset==min_offset:
                #     task.can_move_hoists=[0]
                # elif step.offset==max_offset:
                #     task.can_move_hoists=[num_hoists-1]
                # else:
                #     task.can_move_hoists=list(range(num_hoists)) #todo fix by safe distance
                tasks.append(task)
            rt.append(Job(job_index,tasks))
            #print(rt[-1].x)
        return rt
    def start_job(self):
        if len(self.todo)<1:
            return
        job=random.choice(self.todo)
        self.todo.remove(job)
        logger.info(f'start {job}')
        self.tanks[0].put_job(job)
        return job

    def on_hoist_pickup(self,hoist:Hoist):
        logger.info(f'{hoist} pickup')
        from_tank = self.look_tank_by_hoist(hoist)
        if from_tank!=None:
            job=from_tank.pop_job()
            job.finished_cur_task(from_tank.timer)
            hoist.carring=job
            

    def look_tank_by_hoist(self, hoist):
        from_tank=None
        for tank in self.tanks:
            if tank.plan_hoist==hoist:
                from_tank=tank
        return from_tank

  

    def on_hoist_drop(self,hoist:Hoist):
        job:Job=hoist.carring
        logger.info(f'{hoist} drop')
        if job!=None:
            idx=job.cur_task.cfg.tank_index
            tank=self.tanks[idx]
            hoist.carring=None
            tank.put_job(job)

    def on_scheduling(self,tank:Tank):
        print('on_scheduling',tank)
        tank.plan_hoist=self.hoists[0] #todo
        tank.carring.cur_task.select_hoist=self.hoists[0]
    def on_timeout(self,tank:Tank):
        print('on_timeout',tank)
        self.is_over=True
    def exe(self,hoist_id,cmd:Union[ShiftCommand,TransportCommand]):
        self.hoists[hoist_id].cmd=cmd

    def reset(self):
        self.is_over=False
        self.hoist_sprites=[]
        self.tank_sprites=[]
        self.job_sprites=[]
        self.hoists.clear()
        self.tanks.clear()
        #self.objs:List[GameObject]=[]
        self.make_hoists()
        self.make_tanks()
        self.jobs=self.make_jobs()
        self.todo=[]
        self.todo.extend(self.jobs)
        assert self.num_jobs==len(self.jobs)

    def make_tanks(self):
        for i,offset in enumerate(self.problem.tank_offsets):
            obj=GameObject()
            t:Tank=obj.add_component(Tank)
            t.index=i
            t.x=offset
            t.center=self.center
            self.tanks.append(t)

    def make_hoists(self):
        for i in range(self.num_hoists):
            obj=GameObject()
            h=obj.add_component(Hoist)
            h.code=f'H{i+1}'
            h.center=self.center
            if i==0:
                h.x=self.problem.min_offset
            elif i==self.num_hoists-1:
                h.x=self.problem.max_offset
            else:
                h.x=self.problem.min_offset+G.HOIST_SAFE_DISTANCE*i
            h.fsm.add_state(FreeState(h))
            h.fsm.add_state(MovingState(h))
            h.fsm.add_state(LoweringState(h))
            h.fsm.add_state(LiftingState(h))
            h.fsm.set_state('FreeState')
            self.hoists.append(h)
        

    def update(self,dt,t):
        if self.is_over:
            return
        for h in self.hoists:
            h.game_object.update(dt,t)
        for t in self.tanks:
            t.game_object.update(dt,t)
        for h1 in self.hoists:
            for h2 in self.hoists:
                if h1==h2:
                    continue
                dis=round(abs(h1.x-h2.x))
                
                if (dis<G.HOIST_SAFE_DISTANCE):
                    print(h1,h2,dis)
                    if isinstance(h1.cmd,TransportCommand) and isinstance(h2.cmd,TransportCommand):
                        if h1.cmd.urgency>h2.cmd.urgency:
                            self.avoid(h2, h1)     
                        elif h2.cmd.urgency>h1.cmd.urgency:
                            self.avoid(h1, h2)     
                        else:
                            self.is_over=True
                            self.center.publish('on_hited',self)
                            return
                    elif isinstance(h1.cmd,TransportCommand):
                        if not self.avoid(h2, h1):
                            return                    
                    elif isinstance(h2.cmd,TransportCommand):
                       if not  self.avoid(h1, h2):
                           return
                    else:
                        self.avoid(h1, h2)  
                    

    def avoid(self, h1:Hoist, h2:Hoist):
        dx=h1.x-h2.x
        dx=dx/abs(dx+G.EPS)
        s=h1.fsm.current_state
        if isinstance(s,FreeState) or isinstance(s,MovingState):
            h1.x+=dx
            print(f'{h2}-->{h1}')
            return True
        print(f'{h1} buzy!')
        self.is_over=True
        return False
    
    def render(self,batch):
        if len(self.hoist_sprites)<=0:
            for j in self.hoists:
                self.hoist_sprites.append(BorderedRectangle(0,0,48,24,color=(0,255,0,100),batch=batch))
                #self.sprites.append(
        if len(self.tank_sprites)<=0:
            for t in self.tanks:
                self.tank_sprites.append(Circle(0,0,20,batch=batch))
        if len(self.job_sprites)<=0:
            for j in self.jobs:
                self.job_sprites.append(Circle(0,0,10,color=(250,0,0,200),batch=batch))
        for i,sp in enumerate(self.hoist_sprites):
            j:Hoist=self.hoists[i]
            sp.x=(j.x+1)*64
            sp.y=(j.y+1)*64
                
        for i,sp in enumerate(self.tank_sprites):
            t:Tank=self.tanks[i]
            sp.x=(t.x+1)*64
            sp.y=64

        for i,sp in enumerate(self.job_sprites):
            j:Job=self.jobs[i]
            sp.x=(j.x+1)*64
            sp.y=(j.y+1)*64