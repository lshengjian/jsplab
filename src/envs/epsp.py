from typing import List, Tuple, Dict, Any
from numpy.typing import NDArray
import numpy as np
import copy
from collections import defaultdict
from gymnasium import spaces
import gymnasium as gym
from src.core import Task,convert2fjsp_data,OverHeadCrane,JobShop

EPS=1e-10
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
    def __init__(self, args: Dict, data: List[List[Task]],render_mode=None):
        self.render_mode = render_mode
        # import data containing all instances
        self.batch_data: List[List[Task]] = data
        self.first_crane_index=args.get('first_crane_index', 999)
        self.machine_names:List[str]=args.get('machine_names', [])
        self.num_machines: int = len(self.batch_data[0][0].machines)
        self.max_machines_per_task=0
        self.machine_offsets: Any = args.get('machine_offsets', [])

        self.cranes:Dict[OverHeadCrane]={}
        for i in range(self.first_crane_index,self.num_machines):
            self.cranes[i]=OverHeadCrane(i,self.machine_offsets[i],self.machine_names[i])
        self.js=JobShop(self.cranes.values())
        # retrieve run-dependent settings from config
        self.shuffle: bool = args.get('shuffle', False)
        self.log_interval: int = args.get('log_interval', 10) 
        #self.iterations_over_data = -1 
        self.runs: int = -2  # counts runs (episodes/dones).  because reset is called twice before start    
        self.data_idx: int = 0  
        # reward parameters
        self.reward_strategy = args.get('reward_strategy', 'dense_makespan_reward')
        self.reward_scale = args.get('reward_scale', 1)
        self.mr2_reward_buffer: List[List] = [[] for _ in range(len(data))]  # needed for m2r reward only

        self.set_instance_info()
        self.machine_tasks:Dict[int,List[Task]]=defaultdict(list)
        
        self.num_steps_max: int = args.get('num_steps_max', self.max_num_jobs * self.max_num_tasks*2)
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
        job_id=action
        selected_job_vector = self.to_one_hot(job_id, self.max_num_jobs)
        self.action_history.append(action)
        _, selected_task = self.get_selected_task(job_id)
        # size=len(selected_task.eligible_machines)
        # machine_id=selected_task.eligible_machines[machine_idx%size]#self.choose_machine(selected_task)
        machine_id=self.choose_machine(selected_task)

        # check if the action is valid/executable
        if self.check_valid_job_action(selected_job_vector, self.last_mask):
            # if the action is valid/executable/schedulable
            cur_job_task_index=selected_task.index
            # selected_machine = self.choose_machine(selected_task)
            if cur_job_task_index>0:#不是第一个上料工序
                agv_task_index=self.task_job_mapping[(job_id,cur_job_task_index)]
                agv_task=self.tasks[agv_task_index]
                pre_op_task_idx = self.task_job_mapping[(job_id,cur_job_task_index-1)]
                pre_op_task = self.tasks[pre_op_task_idx]
                next_op_task_idx = self.task_job_mapping[(job_id,cur_job_task_index+1)]
                next_op_task = self.tasks[next_op_task_idx]
                agv_id=machine_id

                agv=self.cranes[machine_id]
                

                x1=self.machine_offsets[pre_op_task.selected_machine]
                machine_id=self.choose_machine(next_op_task)
                x2=self.machine_offsets[machine_id]
  
                
                self.execute_action(job_id, agv_task, agv_id,agv,x1,x2)
                selected_task=next_op_task
                #self.offsets[next_op_task.eligible_machines[agv_index]]
            self.execute_action(job_id, selected_task, machine_id)

            
        else:
            # if the action is not valid/executable/scheduable
            print('invalid action:',action)

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
        if not self.js.is_safe(self.get_makespan()):
            done=True
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
        m_id= int(np.argmin(machine_times))
        # for idx,id in enumerate(task.eligible_machines):
        #     if id==m_id:
        #         return idx
        return m_id
    
    def execute_action(self, job_id: int, task: Task, machine_id: int,agv:OverHeadCrane=None,x1:int=-1,x2:int=-1) -> bool:
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

        
        task.selected_machine = machine_id
        #x0=agv.offset
        
        start_time = max(start_time_of_preceding_task, self.ends_of_machine_occupancies[machine_id])
        if agv!=None:
            dt=agv.move(start_time,x1,x2)
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
        #print(task,task.selected_machine,self.get_makespan())
        return True


    def get_selected_task(self, job_idx: int) -> Tuple[int, Task]:
        """
        Helper Function to get the selected task (next possible task) only by the job index

        :param job_idx: job index

        :return: Index of the task in the task list and the selected task

        """
        task_idx = self.task_job_mapping[(job_idx, self.job_task_state[job_idx])]
        selected_task = self.tasks[task_idx]
        return task_idx, selected_task
    
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
