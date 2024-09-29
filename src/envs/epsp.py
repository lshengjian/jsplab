from typing import List, Tuple, Dict, Any
from numpy.typing import NDArray
import numpy as np

from gymnasium import spaces
import gymnasium as gym
from src.core import Task,Hoist,JobShop
from src.core.hoist_state import make_hoist_states
from src.utils import console
from rich.text import Text
from src.datadef import G
import time
import logging

logger = logging.getLogger(__name__.split('.')[-1])

NUM_SPACE=6
def print_info(info):
    console.print('',end='\r')
    for s in info:
        console.print(s,end='')

class ElectroplateJobShopEnv(gym.Env):
    """
    Scheduling environment for secheduling optimization according to
    https://www.sciencedirect.com/science/article/pii/S0952197622001130.
    """

    #def __init__(self, ins: Instance, data: List[List[Task]],render_mode=None,max_steps=30,safe_distance=2):
    def __init__(self,shop:JobShop,min_num_job=1,max_num_job=10,render_mode=None):
        self.render_mode = render_mode
        self.shop=shop
        self.min_num_job=min_num_job
        self.max_num_job=max_num_job
        #self._makespan=0
        # reward parameters
        #self.reward_strategy ='mr2_reward'# 'dense_makespan_reward'
        self.reward_scale =  1
        self.mr2_reward_buffer: List = [] 
        self._state_obs: NDArray 

    @property
    def makespan(self):
        return self.shop.last_time
      


    def step(self, action: int)-> (List[float], float, bool,bool, Dict):
        """
        Step Function

        :param action: Action to be performed on the current state of the environment
        :return: Observation, reward, done,timeout, infos

        """
 
        # transform and store action
        #job_id=action//self.max_machines_per_task
        #machine_idx=action%self.max_machines_per_task #只是加工任务
        job_id=action 
        job=self.shop.jobs[job_id]
        cur_op_task, agv_task ,next_op_task= self.get_tasks_job(job_id)
        if job.selected_machine!=None:
            m1=job.selected_machine
        else:
            machine_id=self.shop.choose_machine(cur_op_task)
            m1=self.shop.machines[machine_id]
        agv=None
        m2=None
        done=False
        if agv_task!=None:
            m_id=self.shop.choose_machine(agv_task)
            agv=self.shop.machines[m_id]
        if next_op_task!=None:
            m_id=self.shop.choose_machine(next_op_task)
            m2=self.shop.machines[m_id]
        # if m1 is None  or (not cur_op_task.is_last and (agv is None or m2 is None)):
        #     done=True
        #     reward=-0.5
        
        job.assign(agv,m1,m2)
        job.selected_machine=m2
        if self.shop.is_lock(m1.index):
            self.shop.unlock(m1)
        if m2!=None:
            self.shop.lock(m2)

        action_mask = self.get_action_mask()
        infos = {'mask': action_mask}
        observation = self.state_obs
        reward = self.compute_reward()
        done = self.check_done()
        self.num_steps += 1
        time_out=self.num_steps >= self.shop.instance.max_steps
        if not self.shop.is_safe(self.makespan):
            done=True
            reward=-1
            logger.error('cranes hited!')
        
        if done and reward>=0:
            logger.info(f'makespan:{self.makespan}')

        return observation, reward, done, time_out ,infos

    def reset(self,seed=None, options=None) -> Tuple[NDArray,Dict]:
        super().reset(seed=seed)
        product_ids=self.shop.instance.product_ids
        job_nums_dict={}
        for id in product_ids:
            job_nums_dict[id]=np.random.randint(self.min_num_job,self.max_num_job+1)

        #print(job_nums_dict)
        self.shop.reset(job_nums_dict)
        self.action_space: spaces.Discrete = spaces.Discrete(self.shop.instance.num_jobs) 
        #todo: num_jobs*num_machines

        observation_shape = np.array(self.state_obs).shape
        self.observation_space: spaces.Box = spaces.Box(low=0, high=1, shape=observation_shape)

        self.num_steps=0
        self.last_mask: NDArray = np.zeros(len(self.shop.jobs), dtype=int)
        #self.makespan = 0
        action_mask = self.get_action_mask()
        return self.state_obs,{'mask': action_mask}

    @property
    def state_obs(self) -> NDArray:
        """
        Transforms state (task state and factory state) to gym obs
        Scales the values between 0-1 and transforms to onehot encoding
        Confer https://www.sciencedirect.com/science/article/pii/S0952197622001130 section 4.2.1

        :return: Observation

        """

        # (1) remaining time of operations currently being processed on each machine (not compatible with our offline
        # interaction logic
        # (2) sum of all task processing times still to be processed on each machine
        processing_times_on_machines = np.zeros(self.shop.instance.num_machines)
        # (3) sum of all task processing times left on each job
        processing_times_per_job = np.zeros(self.shop.instance.num_jobs)
        # (4) processing time of respective next task on job (-1 if job is done)
        operation_time_of_next_task_per_job = np.zeros(self.shop.instance.num_jobs)
        # (5) machine used for next task (altered for FJJSP compatability to one-hot encoded multibinary representation)
        machines_for_next_task_per_job = np.zeros((self.shop.instance.num_jobs, self.shop.instance.num_machines)) #todo
        # (6) time passed at any given moment. Not really applicable to the offline scheduling case.

        # feature assembly
        next_tasks = self.shop.get_next_tasks()
        #print(f'len of next_tasks:{len(next_tasks)}')
        for task in self.shop.tasks:
            if task is None:
                continue
            if task.done:
                processing_times_on_machines[task.selected_machine] += task.runtime
                processing_times_per_job[task.job_index] += task.runtime
            elif task == next_tasks[task.job_index]:  # next task of the job
                operation_time_of_next_task_per_job[task.job_index] = task.runtime
                machines_for_next_task_per_job[task.job_index,:] = task.machines
                # if not task.is_last:
                #     job=self.shop.jobs[task.job_index]
                #     agv_task=job.tasks[task.index+1]
                #     next_op_task=job.tasks[task.index+2]


        # # normalization
        max_runtime=self.shop.instance.max_runtime+G.EPS
        #print(f'max_runtime:{max_runtime}')
        processing_times_on_machines /= (len(self.shop.tasks) * max_runtime)
        processing_times_per_job /= (self.shop.instance.max_tasks_per_job * max_runtime)
        operation_time_of_next_task_per_job /= max_runtime

        # observation = np.concatenate([
        #     processing_times_on_machines,
        #     processing_times_per_job,
        #     operation_time_of_next_task_per_job,
        #     machines_for_next_task_per_job.flatten()
        # ])
        num_jobs=self.shop.num_jobs
        num_machine=self.shop.num_machines
        data=np.zeros((num_jobs+2,num_machine+2))
        for i,m in self.shop.machines.items():
            data[0,i]=m.offset/self.shop.instance.max_offset #todo for Transfer
        data[1,:num_machine]=processing_times_on_machines
        data[2:,num_machine]=processing_times_per_job
        data[2:,num_machine+1]=operation_time_of_next_task_per_job 
        data[2:,:num_machine]= machines_for_next_task_per_job  


        self._state_obs = data
        # print(observation.shape)
        # print(observation)
        return self._state_obs

    def get_action_mask(self) -> NDArray:
        """
        Get Action mask
        In this environment, we always treat all actions as valid, because the interaction logic accepts it. Note that
        we only allow non-masked algorithms.
        The heuristics, however, still need the job mask.
        1 -> available
        0 -> not available

        :return: Action mask

        """
        num_jobs=self.shop.instance.num_jobs
        rt=[1]*num_jobs
        for i,job in self.shop.jobs.items():
            if job.done or not self.shop.can_select(job):
                rt[i]=0
        job_mask=np.array(rt,dtype=int)
        self.last_mask = job_mask
        return job_mask


    def compute_reward(self) -> Any:
        """
        Calculates the reward that will later be returned to the agent. Uses the self.reward_strategy string to
        discriminate between different reward strategies. Default is 'dense_reward'.

        :return: Reward

        """
        # if self.reward_strategy == 'dense_makespan_reward':
        #     # dense reward for makespan optimization according to https://arxiv.org/pdf/2010.12367.pdf
        #     reward = self._makespan - self.makespan
        #     self._makespan = self.makespan
        # elif self.reward_strategy == 'sparse_makespan_reward':
        #     reward = self.sparse_makespan_reward()
        # elif self.reward_strategy == 'mr2_reward':
        #     reward = self.mr2_reward()
        # else:
        #     raise NotImplementedError(f'The reward strategy {self.reward_strategy} has not been implemented.')
        reward = self.sparse_makespan_reward()
        reward *= self.reward_scale

        return reward
    


    def get_tasks_job(self, job_idx: int) -> Tuple:
        job=self.shop.jobs[job_idx]
        op_task:Task=job.cur_task
        agv_task:Task=None 
        next_op:Task=None
        if not op_task.is_last:
           #task_idx = self.task_job_mapping[(job_idx,cur_task_idx+1)]  
           agv_task=job.tasks[job.cur_task.index+1]
           next_op=job.tasks[job.cur_task.index+2]
        return op_task, agv_task,next_op
    
    def sparse_makespan_reward(self) -> int:
        """
        Computes the reward based on the final makespan at the end of the episode. Else 0.

        :return: (int) sparse reward

        """
        rt=1e10
        if  self.check_done():
            rt = self.makespan

        return 1/rt

    def mr2_reward(self) -> Any:
        """
        Computes mr2 reward based on https://doi.org/10.1016/j.engappai.2022.104868

        :return: mr2 reward

        """
        if not self.check_done():
            reward = 0
        else:
            last_makespan = self.makespan
            if len(self.mr2_reward_buffer) > 0:

                percentile_to_beat = np.percentile(np.array(self.mr2_reward_buffer), 70)

                if last_makespan > percentile_to_beat:
                    reward = -1
                elif last_makespan < percentile_to_beat:
                    reward = 1
                else:
                    if np.random.rand() < 0.1:
                        reward = 1
                    else:
                        reward = -1
            else:
                reward = 0

            self.mr2_reward_buffer.append(last_makespan)
            if len(self.mr2_reward_buffer) > 20:  # pop from left side to update buffer
                self.mr2_reward_buffer.pop(0)


        return reward

    def check_done(self) -> bool:
        """
        Check if all jobs are done

        :return: True if all jobs are done, else False

        """
        return self.shop.check_done()




    def debug(self):
        for i,m in self.shop.machines.items():
            print(f'{m}:',end='')
            for t,task in m.sort_tasks.items():
                print(f'{task}',end=' ')
            print()

    def replay(self):
        pause_time=1.0/G.FPS
        data=[]
        steps=round(self.makespan)
        x1=self.shop.instance.min_offset
        x2=self.shop.instance.max_offset
        for agv in self.shop.cranes:
            tasks=agv.sort_tasks.values()
            moves=[]
            for task in tasks:
                moves.append((task.time_started,task.time_finished))
            flags=make_hoist_states(agv.history,moves,2,2)
            flags=list(map(str,flags))
            data.append((agv.history,flags))

        offsets=self.shop.instance.machine_offsets
        agv_start=self.shop.instance.first_crane_index 
        info=[Text(f'{i:<{NUM_SPACE}d}', style="bold yellow") for i in range(x1,x2+1)]
        print_info(info)
        console.print()
        mname=' '
        info=[Text(f'{mname:^{NUM_SPACE}s}')]*(x2-x1+1)
        for i,x in enumerate(offsets):
            if i>=agv_start:
                continue
            mname=self.shop.instance.machine_names[i]
            if isinstance(x,list):
                x=x[0]
            #print(mname,x-x1)
            info[x-x1]=Text(f'{mname:<{NUM_SPACE}s}', style="bold green")
        print_info(info)
        console.print()

        for t in range(steps):
            mname=' '
            info=[Text(f'{mname:<{NUM_SPACE}s}')]*(x2-x1+1)
            
            for i,agv in enumerate(data):
                x=agv[0][t]
                dir=agv[1][t]
                m_id=f'H{i+1}{dir}'
                info[x-x1]=Text(f'{m_id:<{NUM_SPACE}s}', style="red")
            for j_id,job in self.shop.jobs.items():
                x=self.shop.get_job_pos(t,job)
                if x>=0:
                    m_id=f'J{j_id+1}'
                    info[x-x1]=Text(f'{m_id:<{NUM_SPACE}s}', style="yellow")
            print_info(info)
            time.sleep(pause_time) 
        console.print()
