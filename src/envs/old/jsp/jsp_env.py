import bisect
import datetime
import random
from typing import List
import pandas as pd
import gymnasium as gym
import numpy as np
from src.core import JSP_Data, OperateType
from pathlib import Path


class JspEnv(gym.Env):
    def __init__(self, data: JSP_Data, render_mode=None):
        self.render_mode = render_mode
        """
        This environment model the job shop scheduling problem as a single agent problem:

        -The actions correspond to a job allocation + one action for no allocation at this time step (NOPE action)

        -We keep a time with next possible time steps

        -Each time we allocate a job, the end of the job is added to the stack of time steps

        -If we don't have a legal action (i.e. we can't allocate a job),
        we automatically go to the next time step until we have a legal action

        -
        :param data: JSP instance data
        """
        self.instance_matrix: List[List[OperateType]] = data.jobs_data

        # initial values for variables used for instance
        self.nb_jobs = len(self.instance_matrix)
        self.nb_machines = max([task[0]
                               for j in self.instance_matrix for task in j])+1
        # self.instance_matrix = np.zeros((self.nb_jobs, self.nb_machines), dtype=(int, 2))
        self.jobs_op_time = np.zeros(self.nb_jobs, dtype=int)
        self.max_time_op = 0
        self.max_time_jobs = 0
        self.nb_legal_actions = 0
        self.nb_machine_legal = 0
        # initial values for variables used for solving (to reinitialize when reset() is called)
        self.solution = None
        self.last_solution = None
        self.last_time_step = float("inf")
        self.current_time_step = float("inf")
        self.next_time_step = list()
        self.next_jobs = list()
        self.legal_actions = None
        self.time_until_available_machine = None
        self.time_until_finish_current_op_jobs = None
        self.todo_time_job_task = None
        self.total_perform_op_time_jobs = None
        self.needed_machine_jobs = None
        self.total_idle_time_jobs = None
        self.idle_time_jobs_last_op = None
        self.state = None
        self.illegal_actions = None
        self.action_illegal_no_op = None
        self.machine_legal = None
        # initial values for variables used for representation
        self.start_timestamp = datetime.datetime.now().timestamp()
        self.sum_op = 0
        for job, tasks in enumerate(self.instance_matrix):
            for i, task in enumerate(tasks):
                machine, duration = task
                print(f'J-{i+1} ({machine},{duration})')
                # self.instance_matrix[job][i] = (machine, duration)
                self.max_time_op = max(self.max_time_op, duration)
                self.jobs_op_time[job] += duration
                self.sum_op += duration
        self.max_time_jobs = max(self.jobs_op_time)
        # check the parsed data are correct
        assert self.max_time_op > 0
        assert self.max_time_jobs > 0
        assert self.nb_jobs > 0
        assert self.nb_machines > 1, "We need at least 2 machines"
        assert self.instance_matrix is not None
        # allocate a job + one to wait
        self.action_space = gym.spaces.Discrete(self.nb_jobs + 1)
        # used for plotting
        self.colors = [
            tuple([random.random() for _ in range(3)]) for _ in range(self.nb_machines)
        ]
        """
        matrix with the following attributes for each job:
            -Legal job
            -Left over time on the current op
            -Current operation %
            -Total left over time
            -When next machine available
            -Time since IDLE: 0 if not available, time otherwise
            -Total IDLE time in the schedule
        """
        self.observation_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=(self.nb_jobs*7,), dtype=float
        )
        # self.observation_space = gym.spaces.Dict(
        #     {
        #         "action_mask": gym.spaces.Box(0, 1, shape=(self.nb_jobs + 1,)),
        #         "real_obs": gym.spaces.Box(
        #             low=0.0, high=1.0, shape=(self.nb_jobs, 7), dtype=float
        #         ),
        #     }
        # )

    def _get_current_state_representation(self):

        self.state[:, 0] = self.legal_actions[:-1]
        # print(self.legal_actions,self.state[:, 0])
        return self.state.reshape(-1)

    def get_legal_actions(self):
        return self.legal_actions

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_time_step = 0
        self.next_time_step = list()
        self.next_jobs = list()
        self.nb_legal_actions = self.nb_jobs
        self.nb_machine_legal = 0
        # represent all the legal actions
        self.legal_actions = np.ones(self.nb_jobs + 1, dtype=int)
        self.legal_actions[self.nb_jobs] = 0
        # used to represent the solution
        self.solution = np.full(
            (self.nb_jobs, self.nb_machines), -1, dtype=int)
        self.time_until_available_machine = np.zeros(
            self.nb_machines, dtype=int)
        self.time_until_finish_current_op_jobs = np.zeros(
            self.nb_jobs, dtype=int)
        self.todo_time_job_task = np.zeros(self.nb_jobs, dtype=int)
        self.total_perform_op_time_jobs = np.zeros(self.nb_jobs, dtype=int)
        self.needed_machine_jobs = np.zeros(self.nb_jobs, dtype=int)
        self.total_idle_time_jobs = np.zeros(self.nb_jobs, dtype=int)
        self.idle_time_jobs_last_op = np.zeros(self.nb_jobs, dtype=int)
        self.illegal_actions = np.zeros(
            (self.nb_machines, self.nb_jobs), dtype=int)
        self.action_illegal_no_op = np.zeros(self.nb_jobs, dtype=int)
        self.machine_legal = np.zeros(self.nb_machines, dtype=int)
        for job in range(self.nb_jobs):
            needed_machine = self.instance_matrix[job][0][0]
            self.needed_machine_jobs[job] = needed_machine
            if not self.machine_legal[needed_machine]:
                self.machine_legal[needed_machine] = 1
                self.nb_machine_legal += 1
        self.state = np.zeros((self.nb_jobs, 7), dtype=float)
        return self._get_current_state_representation(), {"action_mask": self.legal_actions}

    def _prioritization_non_final(self):
        if self.nb_machine_legal >= 1:
            for machine in range(self.nb_machines):
                if self.machine_legal[machine]:
                    final_job = list()
                    non_final_job = list()
                    min_non_final = float("inf")
                    for job in range(self.nb_jobs):
                        if (
                            self.needed_machine_jobs[job] == machine
                            and self.legal_actions[job]
                        ):
                            if self.todo_time_job_task[job] == (self.nb_machines - 1):
                                final_job.append(job)
                            else:
                                current_time_step_non_final = self.todo_time_job_task[
                                    job
                                ]
                                time_needed_legal = self.instance_matrix[job][
                                    current_time_step_non_final
                                ][1]
                                machine_needed_nextstep = self.instance_matrix[job][
                                    current_time_step_non_final + 1
                                ][0]
                                if (
                                    self.time_until_available_machine[
                                        machine_needed_nextstep
                                    ]
                                    == 0
                                ):
                                    min_non_final = min(
                                        min_non_final, time_needed_legal
                                    )
                                    non_final_job.append(job)
                    if len(non_final_job) > 0:
                        for job in final_job:
                            current_time_step_final = self.todo_time_job_task[job]
                            time_needed_legal = self.instance_matrix[job][
                                current_time_step_final
                            ][1]
                            if time_needed_legal > min_non_final:
                                self.legal_actions[job] = 0
                                self.nb_legal_actions -= 1

    def _check_no_op(self):
        self.legal_actions[self.nb_jobs] = 0
        if (
            len(self.next_time_step) > 0
            and self.nb_machine_legal <= 3
            and self.nb_legal_actions <= 4
        ):
            machine_next = set()
            next_time_step = self.next_time_step[0]
            max_horizon = self.current_time_step
            max_horizon_machine = [
                self.current_time_step + self.max_time_op for _ in range(self.nb_machines)
            ]
            for job in range(self.nb_jobs):
                if self.legal_actions[job]:
                    time_step = self.todo_time_job_task[job]
                    machine_needed = self.instance_matrix[job][time_step][0]
                    time_needed = self.instance_matrix[job][time_step][1]
                    end_job = self.current_time_step + time_needed
                    if end_job < next_time_step:
                        return
                    max_horizon_machine[machine_needed] = min(
                        max_horizon_machine[machine_needed], end_job
                    )
                    max_horizon = max(
                        max_horizon, max_horizon_machine[machine_needed])
            for job in range(self.nb_jobs):
                if not self.legal_actions[job]:
                    if (
                        self.time_until_finish_current_op_jobs[job] > 0
                        and self.todo_time_job_task[job] + 1 < self.nb_machines
                    ):
                        time_step = self.todo_time_job_task[job] + 1
                        time_needed = (
                            self.current_time_step
                            + self.time_until_finish_current_op_jobs[job]
                        )
                        while (
                            time_step < self.nb_machines - 1 and max_horizon > time_needed
                        ):
                            machine_needed = self.instance_matrix[job][time_step][0]
                            if (
                                max_horizon_machine[machine_needed] > time_needed
                                and self.machine_legal[machine_needed]
                            ):
                                machine_next.add(machine_needed)
                                if len(machine_next) == self.nb_machine_legal:
                                    self.legal_actions[self.nb_jobs] = 1
                                    return
                            time_needed += self.instance_matrix[job][time_step][1]
                            time_step += 1
                    elif (
                        not self.action_illegal_no_op[job]
                        and self.todo_time_job_task[job] < self.nb_machines
                    ):
                        time_step = self.todo_time_job_task[job]
                        machine_needed = self.instance_matrix[job][time_step][0]
                        time_needed = (
                            self.current_time_step
                            + self.time_until_available_machine[machine_needed]
                        )
                        while (
                            time_step < self.nb_machines - 1 and max_horizon > time_needed
                        ):
                            machine_needed = self.instance_matrix[job][time_step][0]
                            if (
                                max_horizon_machine[machine_needed] > time_needed
                                and self.machine_legal[machine_needed]
                            ):
                                machine_next.add(machine_needed)
                                if len(machine_next) == self.nb_machine_legal:
                                    self.legal_actions[self.nb_jobs] = 1
                                    return
                            time_needed += self.instance_matrix[job][time_step][1]
                            time_step += 1

    def step(self, action: int):
        reward = 0.0
        if action == self.nb_jobs:  # end
            self.nb_machine_legal = 0
            self.nb_legal_actions = 0
            for job in range(self.nb_jobs):
                if self.legal_actions[job]:
                    self.legal_actions[job] = 0
                    needed_machine = self.needed_machine_jobs[job]
                    self.machine_legal[needed_machine] = 0
                    self.illegal_actions[needed_machine][job] = 1
                    self.action_illegal_no_op[job] = 1
            while self.nb_machine_legal == 0:
                reward -= self.increase_time_step()
            scaled_reward = self._reward_scaler(reward)
            self._prioritization_non_final()
            self._check_no_op()
            return (
                self._get_current_state_representation(),
                scaled_reward,
                self._is_done(),
                False,
                {"action_mask": self.legal_actions}
            )
        else:
            current_time_step_job = self.todo_time_job_task[action]
            machine_needed = self.needed_machine_jobs[action]
            time_needed = self.instance_matrix[action][current_time_step_job][1]
            reward += time_needed
            self.time_until_available_machine[machine_needed] = time_needed
            self.time_until_finish_current_op_jobs[action] = time_needed
            self.state[action][1] = time_needed / self.max_time_op  # 归一化的加工时间
            to_add_time_step = self.current_time_step + time_needed
            if to_add_time_step not in self.next_time_step:
                index = bisect.bisect_left(
                    self.next_time_step, to_add_time_step)
                self.next_time_step.insert(index, to_add_time_step)
                self.next_jobs.insert(index, action)
            self.solution[action][current_time_step_job] = self.current_time_step
            for job in range(self.nb_jobs):
                if (
                    self.needed_machine_jobs[job] == machine_needed
                    and self.legal_actions[job]
                ):
                    self.legal_actions[job] = 0
                    self.nb_legal_actions -= 1
            self.nb_machine_legal -= 1
            self.machine_legal[machine_needed] = 0
            for job in range(self.nb_jobs):
                if self.illegal_actions[machine_needed][job]:
                    self.action_illegal_no_op[job] = 0
                    self.illegal_actions[machine_needed][job] = 0
            # if we can't allocate new job in the current timestep, we pass to the next one
            while self.nb_machine_legal == 0 and len(self.next_time_step) > 0:
                reward -= self.increase_time_step()
            self._prioritization_non_final()
            self._check_no_op()
            # we then need to scale the reward
            scaled_reward = self._reward_scaler(reward)
            return (
                self._get_current_state_representation(),
                scaled_reward,
                self._is_done(),
                False,
                {"action_mask": self.legal_actions}
            )

    def _reward_scaler(self, reward):
        return reward / self.max_time_op

    def increase_time_step(self):
        """
        The heart of the logic his here, we need to increase every counter when we have a nope action called
        and return the time elapsed
        :return: time elapsed
        """
        hole_planning = 0
        next_time_step_to_pick = self.next_time_step.pop(0)
        self.next_jobs.pop(0)
        difference = next_time_step_to_pick - self.current_time_step
        self.current_time_step = next_time_step_to_pick
        for job in range(self.nb_jobs):
            was_left_time = self.time_until_finish_current_op_jobs[job]
            if was_left_time > 0:
                performed_op_job = min(difference, was_left_time)
                self.time_until_finish_current_op_jobs[job] = max(
                    0, self.time_until_finish_current_op_jobs[job] - difference
                )
                self.state[job][1] = (
                    self.time_until_finish_current_op_jobs[job] /
                    self.max_time_op
                )
                self.total_perform_op_time_jobs[job] += performed_op_job
                self.state[job][3] = (
                    self.total_perform_op_time_jobs[job] / self.max_time_jobs
                )
                if self.time_until_finish_current_op_jobs[job] == 0:
                    self.total_idle_time_jobs[job] += difference - \
                        was_left_time
                    self.state[job][6] = self.total_idle_time_jobs[job] / self.sum_op
                    self.idle_time_jobs_last_op[job] = difference - \
                        was_left_time
                    self.state[job][5] = self.idle_time_jobs_last_op[job] / self.sum_op
                    self.todo_time_job_task[job] += 1
                    self.state[job][2] = self.todo_time_job_task[job] / \
                        self.nb_machines
                    if self.todo_time_job_task[job] < self.nb_machines:
                        self.needed_machine_jobs[job] = self.instance_matrix[job][
                            self.todo_time_job_task[job]
                        ][0]
                        self.state[job][4] = (
                            max(
                                0,
                                self.time_until_available_machine[
                                    self.needed_machine_jobs[job]
                                ]
                                - difference,
                            )
                            / self.max_time_op
                        )
                    else:
                        self.needed_machine_jobs[job] = -1
                        # this allow to have 1 is job is over (not 0 because, 0 strongly indicate that the job is a
                        # good candidate)
                        self.state[job][4] = 1.0
                        if self.legal_actions[job]:
                            self.legal_actions[job] = 0
                            self.nb_legal_actions -= 1
            elif self.todo_time_job_task[job] < self.nb_machines:
                self.total_idle_time_jobs[job] += difference
                self.idle_time_jobs_last_op[job] += difference
                self.state[job][5] = self.idle_time_jobs_last_op[job] / self.sum_op
                self.state[job][6] = self.total_idle_time_jobs[job] / self.sum_op
        for machine in range(self.nb_machines):
            if self.time_until_available_machine[machine] < difference:
                empty = difference - self.time_until_available_machine[machine]
                hole_planning += empty
            self.time_until_available_machine[machine] = max(
                0, self.time_until_available_machine[machine] - difference
            )
            if self.time_until_available_machine[machine] == 0:
                for job in range(self.nb_jobs):
                    if (
                        self.needed_machine_jobs[job] == machine
                        and not self.legal_actions[job]
                        and not self.illegal_actions[machine][job]
                    ):
                        self.legal_actions[job] = 1
                        self.nb_legal_actions += 1
                        if not self.machine_legal[machine]:
                            self.machine_legal[machine] = 1
                            self.nb_machine_legal += 1
        return hole_planning

    def _is_done(self):
        if self.nb_legal_actions == 0:
            self.last_time_step = self.current_time_step
            self.last_solution = self.solution
            return True
        return False

    def render(self):
        df = []
        for job in range(self.nb_jobs):
            i = 0
            while i < self.nb_machines and self.solution[job][i] != -1:
                dict_op = dict()
                dict_op["Task"] = "Job {}".format(job)
                start_sec = self.start_timestamp + self.solution[job][i]
                finish_sec = start_sec + self.instance_matrix[job][i][1]
                dict_op["Start"] = datetime.datetime.fromtimestamp(start_sec)
                dict_op["Finish"] = datetime.datetime.fromtimestamp(finish_sec)
                dict_op["Resource"] = "Machine {}".format(
                    self.instance_matrix[job][i][0]
                )
                df.append(dict_op)
                i += 1
        # fig = None
        if len(df) > 0:
            df = pd.DataFrame(df)
            # fig = ff.create_gantt(
            #     df,
            #     index_col="Resource",
            #     colors=self.colors,
            #     show_colorbar=True,
            #     group_tasks=True,
            # )
            # fig.update_yaxes(
            #     autorange="reversed"
            # )  # otherwise tasks are listed from the bottom up
        return df
