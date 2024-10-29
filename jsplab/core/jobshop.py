
from jsplab.core import *
from jsplab.conf import MultiHoistProblem,G
from jsplab.cbd import GameObject,EventManager
from typing import List,Union
import logging,math,random

from pyglet.shapes import Circle,BorderedRectangle
logger = logging.getLogger(__name__.split('.')[-1])

class JobShop:
    def __init__(self,p:MultiHoistProblem):
        self.problem:MultiHoistProblem=p
        self.num_jobs=len(p.procs)
        self.hoists:List[Hoist]=[]
        self.tanks:List[Tank]=[]
        self.center=EventManager()
        self.center.subscribe('on_start_tank_empty',self.on_start_tank_empty)
        self.center.subscribe('on_scheduling',self.on_scheduling)
        self.center.subscribe('on_timeout',self.on_timeout)
        self.center.subscribe('on_hoist_pickup',self.on_hoist_pickup)
        self.center.subscribe('on_hoist_drop',self.on_hoist_drop)
        self.reset()
    
    @property 
    def num_hoists(self)->int:
        return self.problem.num_hoists
    def on_start_tank_empty(self,tank):
        self.start_job()
    def make_jobs(self):
        cfg:MultiHoistProblem=self.problem
        #num_hoists=self.num_hoists
        
        min_offset,max_offset=self.problem.min_offset,self.problem.max_offset
        rt=[]
        for job_index,proc in enumerate(cfg.procs):
            tasks=[]
            for step in proc:
                task=Task(step)
                task.can_move_hoists=self.problem.select_hoists_by_offset(step.offset)
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
        # job=random.choice(self.todo)
        # self.todo.remove(job)
        job=self.todo.pop(0)
        logger.info(f'start {job}')
        self.tanks[0].put_job(job)

        return job

    def on_hoist_pickup(self,hoist:Hoist):
        #from_tank = self.look_tank_by_hoist(hoist)
        #print(hoist.cmd)
        cmd:TransportCommand=hoist.cmd
        from_tank=self.tanks[cmd.tank1_index]
        if from_tank!=None:
            job=from_tank.pop_job()
            logger.info(f'{hoist} pickup {job}')
            
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
        
        if job!=None:
            logger.info(f'{hoist} drop')
            idx=job.cur_task.cfg.tank_index
            tank=self.tanks[idx]
            hoist.carring=None
            tank.put_job(job)

    def on_scheduling(self,tank:Tank):
       
        for h in self.cmds:
            if len(self.cmds[h])<1:
                continue
            cmd:TransportCommand=self.cmds[h][0]
            if cmd.tank1_index==tank.index:
                tank.carring.cur_task.select_hoist=self.hoists[h]
                logger.info(f'scheduling {self.hoists[h].code} for {tank}')
                break
        
    def on_timeout(self,tank:Tank):
        print('on_timeout',tank)
        self.is_over=True

    def send_command(self):
        cmds=self.cmds
        for h in cmds:
            if self.hoists[h].cmd is None and len(cmds[h])>0:
                cmd:TransportCommand=cmds[h][0]
                job:Job=self.tanks[cmd.tank1_index].carring
                if job!=None and job.cur_task.select_hoist==self.hoists[h]:
                    self.hoists[h].cmd=cmd
                    cmds[h].pop(0)


        

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

        self.jobs=self.make_jobs()
        self.todo=[]
        self.todo.extend(self.jobs)
        self.make_hoists()
        self.make_tanks()
        assert self.num_jobs==len(self.jobs)


    def make_tanks(self):
        for i,offset in enumerate(self.problem.tank_offsets):
            obj=GameObject()
            t:Tank=obj.add_component(Tank)
            t.index=i
            t.x=offset
            t.center=self.center
            self.tanks.append(t)
            t.reset()
            
            

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
            h.min_x=self.problem.min_offset+i*G.HOIST_SAFE_DISTANCE
            k=self.num_hoists-1-i
            h.max_x=self.problem.max_offset-k*G.HOIST_SAFE_DISTANCE
            h.fsm.add_state(FreeState(h))
            h.fsm.add_state(MovingState(h))
            h.fsm.add_state(LoweringState(h))
            h.fsm.add_state(LiftingState(h))
            h.fsm.set_state('FreeState')
            self.hoists.append(h)
        

    def update(self,dt,t):
        if self.is_over:
            return
        self.send_command()
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
                        self.avoid(h2, h1)           
                    elif isinstance(h2.cmd,TransportCommand):
                       self.avoid(h1, h2)
                    else:
                        self.avoid(h1, h2)  
                    

    def avoid(self, h1:Hoist, h2:Hoist):
        dx=h1.x-h2.x
        dx=dx/abs(dx+G.EPS)
        s=h1.fsm.current_state
        if isinstance(s,FreeState) or isinstance(s,MovingState):
            h1.x+=dx
            logger.info(f'{h2}-->{h1}')
            if h1.x<h1.min_x or h1.x>h1.max_x:
                self.is_over=True
                logger.error(f'{h1} out bound!')
                return
        logger.error(f'{h1} buzy! {h2} hited!')
        self.is_over=True

    
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
                self.job_sprites.append(Circle(0,0,10,color=(250,234,60,200),batch=batch))
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