
from jsplab.core import *
from jsplab.conf import MultiHoistProblem,G
from jsplab.cbd import GameObject,EventManager
from typing import List,Union,Dict
import numpy as np
from numpy.typing import NDArray
import logging
from collections import defaultdict
logger = logging.getLogger(__name__.split('.')[-1])

class MultiHoistJobShop:
    def __init__(self,p:MultiHoistProblem):
        self.problem:MultiHoistProblem=p
        self.num_jobs=len(p.procs)
        self.hoists:List[Hoist]=[]
        self.tanks:List[Tank]=[]
        self.jobs=[]
        self.job_seq_tasks=[]
        self.center=EventManager()
        self.center.subscribe('on_start_tank_empty',self.on_start_tank_empty)
        self.center.subscribe('on_scheduling',self.on_scheduling)
        self.center.subscribe('on_timeout',self.on_timeout)
        self.center.subscribe('on_hoist_pickup',self.on_hoist_pickup)
        self.center.subscribe('on_hoist_drop',self.on_hoist_drop)
        

    def cost(self,X:NDArray)->float:
        self.reset()
        self.cmds=self.get_solution_info(X)
        rt=None
        t=1
        while len(self.jobs)>0:
            self.update(1)
            t+=1
            if self.is_over:
                rt=99999
                break
            rt=t
        return rt
    def get_move_task_hoists(self):
        hs={}
        for job_idx,job in enumerate(self.jobs):
            for i in range(1,len(job.tasks)):
                idx=job_idx*100+i-1
                t1:Task=job.tasks[i-1]
                t2:Task=job.tasks[i]
                mi_hs=set(t1.can_move_hoists)&set(t2.can_move_hoists)
                hs[idx]=list(mi_hs)
        return hs

    def get_solution_info(self,X:NDArray)->Dict[int,List[TransportCommand]]:
        #X=X.reshape(self.shape)
        xs=X[0]
        idxs=np.argsort(xs)
        seqs=np.array(self.job_seq_tasks,dtype=int)
        job_idxs=seqs[idxs]
        hoist_index=np.argmin(X[1:],axis=0)#有可能操作本任务的机器范围！
        cmds=defaultdict(list)
        cur_move_idx={}
        hs=self.get_move_task_hoists()
            
        for m,job_idx in enumerate(job_idxs):
            if not (job_idx  in cur_move_idx):
                cur_move_idx[job_idx]=0
            else:
                cur_move_idx[job_idx]+=1
            mi=cur_move_idx[job_idx]
            job=self.jobs[job_idx]
            t1:Task=job.tasks[mi]
            t2:Task=job.tasks[mi+1]
            cmd=TransportCommand(t1.cfg.tank_index,t2.cfg.tank_index,t1.cfg.offset,t2.cfg.offset)
            hoists=hs[job_idx*100+mi]
            cmds[hoists[hoist_index[m]%len(hoists)]].append(cmd)
        return cmds
 
    def make_random_solution(self):
        size=len(self.job_seq_tasks)
        data=np.random.random((3,size))
        return data
    @property 
    def num_hoists(self)->int:
        return self.problem.num_hoists
    def on_start_tank_empty(self,tank):
        self.should_add_new_job=True
    def make_jobs(self):
        cfg:MultiHoistProblem=self.problem
        #num_hoists=self.num_hoists
        
        #min_offset,max_offset=self.problem.min_offset,self.problem.max_offset
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
            job.finished_cur_task(from_tank.timer)
            logger.info(f'{hoist} pickup {job}')
            hoist.carring=job

            

    def look_tank_by_hoist(self, hoist):
        from_tank=None
        for tank in self.tanks:
            if tank.plan_hoist==hoist:
                from_tank=tank
        return from_tank

  

    def on_hoist_drop(self,hoist:Hoist,job:Job):
        
        if job!=None:
            logger.info(f'{hoist} drop')
            idx=job.cur_task.cfg.tank_index
            tank=self.tanks[idx]
            hoist.carring=None
            if idx!=len(self.tanks)-1:
                tank.put_job(job)
            else:
                self.jobs.remove(job)
                if len(self.todo)==0:
                    logger.info(f'all jobs finished! time:{self.timer}')
                    #self.is_over=True


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
        self.timer=0
        self.is_over=False
        self.should_add_new_job=True

        self.hoists.clear()
        self.tanks.clear()
        #self.objs:List[GameObject]=[]

        self.jobs.clear()
        self.jobs.extend(self.make_jobs())
        self.job_seq_tasks.clear()
        job_starts={0:0}
        total=0
        for j_idx,job in enumerate(self.jobs):
            js=[j_idx]*(len(job.tasks)-1) #两个加工之间一次搬运
            job_starts[j_idx]=total
            total+=len(js)
            self.job_seq_tasks.extend(js)
        self.start_task_job=job_starts
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
            #t.reset()
            
            

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
            obj.add_component(HoistRecord)
            h.fsm.add_state(FreeState(h))
            h.fsm.add_state(MovingState(h))
            h.fsm.add_state(LoweringState(h))
            h.fsm.add_state(LiftingState(h))
            h.fsm.set_state('FreeState')
            self.hoists.append(h)
        

    def update(self,dt):
        self.timer+=dt
        t=self.timer
        if self.is_over:
            return
        if self.should_add_new_job:
            self.should_add_new_job=False
            self.start_job()
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
                    #logger.info(h1,h2,dis)
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
            if h1.x<h1.min_x-0.1 or h1.x>h1.max_x+0.1:
                self.is_over=True
                logger.error(f'{h1} out bound!')
                return
        else:
            logger.error(f'{h1} buzy! {h2} hited!')
            self.is_over=True

    
