from typing import List, Tuple, Dict, Any
from numpy.typing import NDArray
import numpy as np
import copy
from collections import defaultdict
from gymnasium import spaces
import gymnasium as gym
from src.core import Instance,get_max_steps,Task,convert2fjsp_data,OverHeadCrane,JobShop
from src.core.crane_state import make_crane_states
from src.utils import console
from rich.text import Text
import time
from ..core import JobShop
NUM_SPACE=5
def print_info(info):
    console.print('',end='\r')
    for s in info:
        console.print(s,end='')

class ElectroplateJobShopEnv(gym.Env):
    """
    Scheduling environment for secheduling optimization according to
    https://www.sciencedirect.com/science/article/pii/S0952197622001130.

    Main differences to the vanilla environment:

    - ACTION: Indirect action mapping
    - REWARD: m-r2 reward (which means we have to train on the same data again and again)
    - OBSERVATION: observation different ("normalization" looks like division by max to [0, 1] in paper code). Not every
      part makes sense, due to the different interaction logic
    - INTERACTION LOGIC WARNING:
    - original paper: time steps are run through, the agent can take as many actions as it wants per time-step,
      but may not schedule into the past.
    - our adaptation: we still play tetris, meaning that we schedule whole blocks of work at a time

    :param config: Dictionary with parameters to specify environment attributes
    :param data: Scheduling problem to be solved, so a list of instances

    """
    EPS=1e-10
    #def __init__(self, ins: Instance, data: List[List[Task]],render_mode=None,max_steps=30,safe_distance=2):
    def __init__(self,shop:JobShop,render_mode=None):
        self.render_mode = render_mode

        #self.batch_data: List[List[Task]] = data
        # self.first_crane_index=ins.first_crane_index 
        # self.machine_names:List[str]=ins.machine_names
        # self.num_machines: int = ins.num_machines
        # self.max_machines_per_task=ins.max_machines_per_task
        # self.machine_offsets: Any = ins.machine_offsets

        self.shop=shop
        # retrieve run-dependent settings from config
        self.shuffle: bool =True
        self.log_interval: int =10
        #self.iterations_over_data = -1 
        self.runs: int = -2  # counts runs (episodes/dones).  because reset is called twice before start    
        self.data_idx: int = 0  
        # reward parameters
        self.reward_strategy = 'dense_makespan_reward'
        self.reward_scale =  1
        self.mr2_reward_buffer: List[List] = [[] for _ in range(len(data))]  # needed for m2r reward only

        #self.set_instance_info()
        #self.machine_tasks:Dict[int,List[Task]]=defaultdict(list)
        #self.job_tasks:Dict[int,List[Task]]=defaultdict(list)
        
        #self.num_steps_max: int = get_max_steps(ins,2,2,1.6)
        self._state_obs: NDArray = self.reset()[0]
        # training info log updated after each "epoch" over all training data
        self.action_history: List = []  # stores the sequence of tasks taken
        self.executed_job_history: List = []  # stores the sequence of jobs, of which the task is scheduled
        self.reward_history: List = []  # stores the rewards
        self.episodes_rewards: List = []
        self.episodes_makespans: List = []

        self.action_space: spaces.Discrete = spaces.Discrete(self.max_num_jobs*self.max_machines_per_task) 
        # overwrite observation space
        observation_shape = np.array(self.state_obs).shape
        self.observation_space: spaces.Box = spaces.Box(low=0, high=1, shape=observation_shape)
    def debug(self):
        for m,ts in self.machine_tasks.items():
            name=self.machine_names[m]
            offset=self.machine_offsets[m]
            print(f'{name}[{offset}]:',end='')
            for task in ts:
                print(f'{task}',end=' ')
            print()

    def replay(self,pause_time:int):
        data=[]
        steps=self.makespan
        for m_id,agv in self.shop.machines.items():
            tasks=self.machine_tasks[m_id]
            moves=[]
            for task in tasks:
                moves.append((task.time_started,task.time_finished))
            flags=make_crane_states(agv.pos,moves,2,2)
            flags=list(map(str,flags))
            data.append((agv.pos,flags))
        x1=self.instance.min_offset
        x2=self.instance.max_offset
        offsets=self.instance.machine_offsets
        agv_start=self.instance.first_crane_index 
        info=[Text(f'{i:^4d}', style="bold yellow") for i in range(x1,x2+1)]
        print_info(info)
        console.print()
        for t in range(steps):
            m_id=' '
            info=[Text(f'{m_id:^{NUM_SPACE}s}')]*(x2-x1+1)
            #assert len(info)==self.max_x-self.min_x+1
            
            # for i,x in enumerate(offsets):
            #     if i>=agv_start:
            #         continue
            #     m_id=self.instance.machine_names[i]
            #     info[x]=Text(f'{m_id:<{NUM_SPACE}s}', style="bold green")
            #console.print(f'\r{info}',end='')

            for i,agv in enumerate(data):
                x=agv[0][t]
                dir=agv[1][t]
                m_id=f'{i+1}{dir}'
                info[x]=Text(f'{m_id:<{NUM_SPACE}s}', style="red")
            # for j_id in range(self.instance.num_jobs):
            #     x=self.shop.get_job_pos(t,j_id,self.tasks)
            #     if x>=0:
            #         m_id=f'J{j_id+1}'
            #         info[x]=Text(f'{m_id:<{NUM_SPACE}s}', style="yellow")
            print_info(info)
            time.sleep(pause_time) 

    def set_instance_info(self):
        """
        Retrieves info about the instance size and configuration from an instance sample
        :return: (number of jobs, number of tasks and the maximum runtime) of this datapoint
        """
        
        max_job_index, max_task_index, max_runtime,max_machines_task = 0, 0, 0, 0
        for instance in self.batch_data:
            for task in instance:
                if task.job_index>max_job_index:
                    max_job_index=task.job_index
                if task.index>max_task_index:
                    max_task_index=task.index
                if  task.runtime>max_runtime: #task.runtime!=None and
                    max_runtime=task.runtime
                ms=task.eligible_machines
                if len(ms)>max_machines_task:
                    max_machines_task=len(ms)

        self.max_num_jobs=max_job_index + 1
        self.max_num_tasks= max_task_index+ 1
        self.max_runtime=max_runtime
        self.max_machines_per_task=max_machines_task

        


    def step(self, action: int, **kwargs)-> (List[float], Any, bool,bool, Dict):
        """
        Step Function

        :param action: Action to be performed on the current state of the environment
        :param kwargs: should include "action_mode", because the interaction pattern between heuristics and
            the agent are different and need to be processed differently

        :return: Observation, reward, done, infos

        """
        # check if action_mode was set
 
        # transform and store action
        #job_id=action//self.max_machines_per_task
        #machine_idx=action%self.max_machines_per_task #只是加工任务
        job_id=action #天车任务
        #selected_job_vector = self.to_one_hot(job_id, self.max_num_jobs)
        self.action_history.append(action)
        op_task, agv_task = self.get_cur_tasks(job_id)
        # size=len(selected_task.eligible_machines)
        # machine_id=selected_task.eligible_machines[machine_idx%size]#self.choose_machine(selected_task)
        machine_id=self.choose_machine(op_task)
        
        self.execute_action(job_id, op_task, machine_id)
        if agv_task!=None:
            next_op_task_idx = self.task_job_mapping[(job_id,agv_task.index+1)]
            next_op_task = self.tasks[next_op_task_idx]
            agv_id=self.choose_machine(agv_task)
            agv=self.shop.machines[agv_id]
            x1=self.machine_offsets[machine_id]
            #dis=abs(agv.offset-x1)
            machine_id=self.choose_machine(next_op_task)
            x2=self.machine_offsets[machine_id]
            self.execute_action(job_id, agv_task, agv_id,agv,x1,x2)

        # update variables and track reward
        action_mask = self.get_action_mask()
        infos = {'mask': action_mask}
        observation = self.state_obs
        reward = self.compute_reward()
        self.reward_history.append(reward)

        done = self.check_done()
        if done:
            #episode_reward_sum = np.sum(self.reward_history)
            makespan = self.get_makespan()
            print(f'run {self.runs} makespan:',makespan)
            self.episodes_makespans.append(makespan)
            self.episodes_rewards.append(np.mean(self.reward_history))

        self.num_steps += 1
        time_out=self.num_steps == self.num_steps_max
        if not self.shop.is_safe(self.get_makespan()):
            time_out=True
            reward=-10
        return observation, reward, done, time_out ,infos

    def reset(self,seed=None, options=None) -> Tuple[NDArray,Dict]:
        """
        - Resets the episode information trackers
        - Updates the number of runs
        - Loads new instance

        :return: First observation by calling the class function self.state_obs

        """
        super().reset(seed=seed)
        # update runs (episodes passed so far)
        self.runs += 1
        self.num_steps=0
        self.machine_tasks.clear()
        #self.job_tasks.clear()
        # clear episode rewards after all training data has passed once. Stores info across runs.
        if self.data_idx == 0:
            self.episodes_makespans, self.episodes_rewards = ([], [])
            #self.iterations_over_data += 1

        # load new instance every run
        self.data_idx = 0 if self.runs<1 else self.runs % len(self.batch_data)
        self.tasks = copy.deepcopy(self.batch_data[self.data_idx])
        self.total_num_tasks: int = len(self.tasks)
        if self.shuffle:
            np.random.shuffle(self.tasks)
        data=convert2fjsp_data(self.tasks)
        self.num_jobs=len(data)
        self.num_tasks_job: NDArray = np.zeros(self.num_jobs, dtype=int)
        for i,job in enumerate(data):
            self.num_tasks_job[i]=len(job)
        self.max_job_index: int = self.num_jobs - 1
        self.last_mask: NDArray = np.zeros(self.num_jobs, dtype=int)
        self.makespan = 0
        self.ends_of_machine_occupancies: NDArray = np.zeros(self.num_machines, dtype=int)
        #self.tool_occupancies = [[] for _ in range(self.num_tools)]
        self.job_task_state: NDArray = np.zeros(self.num_jobs, dtype=int)
        self.action_history = []
        self.executed_job_history = []
        self.reward_history = []


        self.task_job_mapping:Dict[Tuple[int,int],int] = {(task.job_index, task.index): i for i, task in enumerate(self.tasks)}

        # retrieve maximum deadline of the current instance
        # max_deadline = max([task.deadline for task in self.tasks])
        # self.max_deadline:int = max_deadline if max_deadline > 0 else 1
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
        processing_times_on_machines = np.zeros(self.num_machines)
        # (3) sum of all task processing times left on each job
        processing_times_per_job = np.zeros(self.max_num_jobs)
        # (4) processing time of respective next task on job (-1 if job is done)
        operation_time_of_next_task_per_job = np.zeros(self.max_num_jobs)
        # (5) machine used for next task (altered for FJJSP compatability to one-hot encoded multibinary representation)
        machines_for_next_task_per_job = np.zeros((self.max_num_jobs, self.num_machines))
        # (6) time passed at any given moment. Not really applicable to the offline scheduling case.

        # feature assembly
        next_tasks = self.get_next_tasks()
        for task in self.tasks:
            if task.done:
                processing_times_on_machines[task.selected_machine] += task._runtimes[task.selected_machine]
                processing_times_per_job[task.job_index] += task._runtimes[task.selected_machine]
            elif task == next_tasks[task.job_index]:  # next task of the job
                operation_time_of_next_task_per_job[task.job_index] = task.runtime
                machines_for_next_task_per_job[task.job_index,:] = task.machines

        # normalization
        processing_times_on_machines /= (self.total_num_tasks * self.max_runtime)
        processing_times_per_job /= (self.max_num_tasks * self.max_runtime)
        operation_time_of_next_task_per_job /= self.max_runtime

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
        job_mask = np.where(self.job_task_state < self.num_tasks_job,
                            np.ones(self.num_jobs, dtype=int), np.zeros(self.num_jobs, dtype=int))

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
    def choose_machine(self, task: Task) -> int:
        """
        This function performs the logic, with which the machine is chosen (in the case of the flexible JSSP)
        Implemented at the moment: Choose the machine out of the set of possible machines with the earliest possible
        start time

        :param task: Task

        :return: Machine on which the task will be scheduled.

        """
        possible_machines = task.machines
        machine_times = np.where(possible_machines,
                                 self.ends_of_machine_occupancies,
                                 np.full(len(possible_machines), np.inf))

        return int(np.argmin(machine_times))
    
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


    def get_cur_tasks(self, job_idx: int) -> Tuple:
        cur_task_idx=self.job_task_state[job_idx]
        task_idx = self.task_job_mapping[(job_idx,cur_task_idx )]
        op_task:Task = self.tasks[task_idx]
        agv_task=None 
        if not op_task.is_last:
           task_idx = self.task_job_mapping[(job_idx,cur_task_idx+1)]  
           agv_task=self.tasks[task_idx]
           #print('op task',op_task)
 

        return op_task, agv_task
    
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
        sum_done = sum([task.done for task in self.tasks])
        return sum_done == self.total_num_tasks 

    def get_makespan(self):
        """
        Returns the current makespan (the time the latest of all scheduled tasks finishes)
        """
        return np.max(self.ends_of_machine_occupancies)

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
