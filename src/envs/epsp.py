from typing import List, Tuple, Dict, Any
from numpy.typing import NDArray
import numpy as np

from gymnasium import spaces
import gymnasium as gym
from src.core import Job,Task,OverHeadCrane,JobShop
from src.core.crane_state import make_crane_states
from src.utils import console
from rich.text import Text
from src.datadef import G
import time
NUM_SPACE=5
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
    def __init__(self,shop:JobShop,render_mode=None):
        self.render_mode = render_mode
        self.shop=shop
        # reward parameters
        self.reward_strategy = 'dense_makespan_reward'
        self.reward_scale =  1
        #self.mr2_reward_buffer: List[List] = [[] for _ in range(len(data))]  # needed for m2r reward only
        self._state_obs: NDArray 
    def debug(self):
        for i,m in self.shop.machines.items():
            name=self.shop.instance.machine_names[i]
            offset=self.shop.instance.machine_offsets[i]
            print(f'{m}:',end='')
            for t,task in m.sort_tasks.items():
                print(f'{task}',end=' ')
            print()

    def replay(self,pause_time:int):
        data=[]
        steps=self.makespan
        x1=self.shop.instance.min_offset
        x2=self.shop.instance.max_offset
        for agv in self.shop.cranes:
            tasks=agv.sort_tasks.values()
            moves=[]
            for task in tasks:
                moves.append((task.time_started,task.time_finished))
            flags=make_crane_states(agv.pos,moves,2,2)
            flags=list(map(str,flags))
            data.append((agv.pos,flags))

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

        for t in range(round(steps)):
            mname=' '
            info=[Text(f'{mname:<{NUM_SPACE}s}')]*(x2-x1+1)
            
            for i,agv in enumerate(data):
                x=agv[0][t]
                dir=agv[1][t]
                m_id=f'{i+1}{dir}'
                info[x-x1]=Text(f'{m_id:<{NUM_SPACE}s}', style="red")
            for j_id,job in self.shop.jobs.items():
                x=self.shop.get_job_pos(t,job)
                if x>=0:
                    m_id=f'J{j_id+1}'
                    info[x-x1]=Text(f'{m_id:<{NUM_SPACE}s}', style="yellow")
            print_info(info)
            time.sleep(pause_time) 

       


    def step(self, action: int)-> (List[float], Any, bool,bool, Dict):
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
        op_task, agv_task ,next_task= self.get_tasks_job(job_id)
        if job.selected_machine!=None:
            m1=job.selected_machine
        else:
            machine_id=self.shop.choose_machine(op_task)
            m1=self.shop.machines[machine_id]
        agv=None
        m2=None
        if agv_task!=None:
            agv=self.shop.machines[self.shop.choose_machine(agv_task)]
        if next_task!=None:
            m2=self.shop.machines[self.shop.choose_machine(next_task)]
        job.assign(agv,m1,m2)
        if self.shop.is_lock(m1.index):
            self.shop.unlock(m1)
        if m2!=None:
            self.shop.lock(m2)

        action_mask = self.get_action_mask()
        infos = {'mask': action_mask}
        observation = self.state_obs
        reward = self.compute_reward()
        done = self.check_done()
        if done:
            #episode_reward_sum = np.sum(self.reward_history)
            makespan = self.get_makespan()
            print(f'makespan:',makespan)
            # self.episodes_makespans.append(makespan)
            # self.episodes_rewards.append(np.mean(self.reward_history))

        self.num_steps += 1
        time_out=self.num_steps == self.shop.instance.max_steps
        # if not self.shop.is_safe(self.get_makespan()):
        #     done=True
        #     reward=-10
        return observation, reward, done, time_out ,infos

    def reset(self,seed=None, options={}) -> Tuple[NDArray,Dict]:
        super().reset(seed=seed)
        self.shop.reset(options)
        self.action_space: spaces.Discrete = spaces.Discrete(self.shop.instance.num_jobs) 
        #todo: num_jobs*num_machines

        observation_shape = np.array(self.state_obs).shape
        self.observation_space: spaces.Box = spaces.Box(low=0, high=1, shape=observation_shape)

        self.num_steps=0
        self.last_mask: NDArray = np.zeros(len(self.shop.jobs), dtype=int)
        self.makespan = 0
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
        for task in self.shop.tasks:
            if task.done:
                processing_times_on_machines[task.selected_machine] += task.runtime
                processing_times_per_job[task.job_index] += task.runtime
            elif task == next_tasks[task.job_index]:  # next task of the job
                operation_time_of_next_task_per_job[task.job_index] = task.runtime
                machines_for_next_task_per_job[task.job_index,:] = task.machines

        # # normalization
        max_runtime=self.shop.instance.max_runtime
        processing_times_on_machines /= (len(self.shop.tasks) * max_runtime)
        processing_times_per_job /= (self.shop.instance.max_tasks_job * max_runtime)
        operation_time_of_next_task_per_job /= max_runtime

        observation = np.concatenate([
            processing_times_on_machines,
            processing_times_per_job,
            operation_time_of_next_task_per_job,
            machines_for_next_task_per_job.flatten()
        ])

        self._state_obs = observation
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
            if job.done:
                rt[i]=0
        job_mask=np.array(rt,dtype=int)

        # job_mask = np.where(self.job_task_state < self.num_tasks_job,
        #                     np.ones(self.num_jobs, dtype=int), np.zeros(self.num_jobs, dtype=int))

        self.last_mask = job_mask
        return job_mask

    def get_next_tasks(self):
        """returns the next tasks that can be scheduled"""
        next_tasks = []
        for job in range(self.num_jobs):
            if self.job_task_state[job] == self.num_tasks_job[job]:  # means that job is done
                next_tasks.append(None)
            else:
                task_position = self.task_job_mapping[(job, self.job_task_state[job])]
                next_tasks.append(self.tasks[task_position])
        return next_tasks
    def compute_reward(self) -> Any:
        """
        Calculates the reward that will later be returned to the agent. Uses the self.reward_strategy string to
        discriminate between different reward strategies. Default is 'dense_reward'.

        :return: Reward

        """
        if self.reward_strategy == 'dense_makespan_reward':
            # dense reward for makespan optimization according to https://arxiv.org/pdf/2010.12367.pdf
            reward = self.makespan - self.get_makespan()
            self.makespan = self.get_makespan()
        elif self.reward_strategy == 'sparse_makespan_reward':
            reward = self.sparse_makespan_reward()
        elif self.reward_strategy == 'mr2_reward':
            reward = self.mr2_reward()
        else:
            raise NotImplementedError(f'The reward strategy {self.reward_strategy} has not been implemented.')

        reward *= self.reward_scale

        return reward
    
    def execute_action(self, job_id: int, task: Task, machine_id: int,agv:OverHeadCrane=None,x1:int=-1,x2:int=-1,start=0) -> bool:
        """
        This Function executes a valid action
        - set machine
        - update job and task

        :param job_id: job_id of the task to be executed
        :param task: Task
        :param eligible_machine_idx: index of the eligible machine  on which the task is to be executed

        :return: bool

        """
        # check task preceding in the job (if it is not the first task within the job)
        #machine_id=task.eligible_machines[eligible_machine_idx]
        # if eligible_machine_idx>=len(task.eligible_machines) or task._runtimes[machine_id]<1:
        #     print(f'error action: job_id:{job_id} ,eligible_machine_idx:{eligible_machine_idx}')
        #     return False
        if task.index == 0:
            start_time_of_preceding_task = 0
        else:
            preceding_task = self.tasks[self.task_job_mapping[(job_id, task.index - 1)]]
            start_time_of_preceding_task = preceding_task.time_finished
            if agv is not None and task.index>1:
                start_time_of_preceding_task=preceding_task.time_started

        
        task.selected_machine = machine_id
        #x0=agv.offset
        
        start_time = max(start,start_time_of_preceding_task, self.ends_of_machine_occupancies[machine_id])
        if agv!=None:
            dt=agv.move(x1,x2,start_time)
            #print(f'move:{x1}->{x2} at time:{start_time}')
        else:
            dt=task._runtimes[machine_id]
        task.runtime=dt
        end_time = start_time + dt
        # update machine occupancy and job_task_state
        self.ends_of_machine_occupancies[machine_id] = end_time
        self.job_task_state[job_id] += 1
        # update job and task
        task.time_started = start_time
        task.time_finished = end_time
        
        task.done = True
        self.machine_tasks[machine_id].append(task)
        #self.job_tasks[job_id].append(task)
        #print(f'{task} {self.instance.machine_names[machine_id]}')
        return True


    def get_tasks_job(self, job_idx: int) -> Tuple:
        job=self.shop.jobs[job_idx]
        op_task:Task=job.cur_task
        # cur_task_idx=self.job_task_state[job_idx]
        # task_idx = self.task_job_mapping[(job_idx,cur_task_idx )]
        #op_task:Task = self.tasks[task_idx]
        agv_task:Task=None 
        next_op:Task=None
        if not op_task.is_last:
           #task_idx = self.task_job_mapping[(job_idx,cur_task_idx+1)]  
           agv_task=job.tasks[job.cur_task.index+1]
           next_op=job.tasks[job.cur_task.index+2]
           #print('op task',op_task)
 

        return op_task, agv_task,next_op
    
    def sparse_makespan_reward(self) -> int:
        """
        Computes the reward based on the final makespan at the end of the episode. Else 0.

        :return: (int) sparse reward

        """
        if not self.check_done():
            reward = 1e10
        else:
            reward = self.get_makespan()

        return 1/reward

    def mr2_reward(self) -> Any:
        """
        Computes mr2 reward based on https://doi.org/10.1016/j.engappai.2022.104868

        :return: mr2 reward

        """
        if not self.check_done():
            reward = 0
        else:
            last_makespan = self.get_makespan()
            if len(self.mr2_reward_buffer[self.data_idx]) > 0:

                percentile_to_beat = np.percentile(np.array(self.mr2_reward_buffer[self.data_idx]), 70)

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

            self.mr2_reward_buffer[self.data_idx].append(last_makespan)
            if len(self.mr2_reward_buffer[self.data_idx]) > 20:  # pop from left side to update buffer
                self.mr2_reward_buffer[self.data_idx].pop(0)


        return reward

    def check_done(self) -> bool:
        """
        Check if all jobs are done

        :return: True if all jobs are done, else False

        """
        # sum_done = sum([task.done for task in self.tasks])
        # return sum_done == self.total_num_tasks 
        return self.shop.check_done()

    def get_makespan(self):
        """
        Returns the current makespan (the time the latest of all scheduled tasks finishes)
        """
        # rt=0
        # for t,m in self.shop.machines.items():
        #     if rt<m.last_time:
        #         rt=m.last_time
        # return rt

        return np.max(self.shop.ends_of_machine_occupancies)

    @staticmethod
    def to_one_hot(x: int, max_size: int) -> np.array:
        """
        Convert to One Hot encoding

        :param x: Index which value should be 1
        :param max_size: Size of the one hot encoding vector

        :return: One hot encoded vector

        """
        one_hot = np.zeros(max_size)
        one_hot[x] = 1
        return one_hot

    @staticmethod
    def check_valid_job_action(job_action: NDArray, job_mask: NDArray) -> bool:
        """
        Check if job action is valid

        :param job_action: Job action as one hot vector
        :param job_mask: One hot vector with ones for each valid job

        :return: True if job_action is valid, else False

        """
        return np.sum(job_action == job_mask) >= 1
