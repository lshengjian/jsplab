import os
import time
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optimizer
from torch.distributions import Categorical
from torch.utils.data.sampler import BatchSampler, SubsetRandomSampler
from ..env.fjsp import JobEnv

m_seed = 3407
# 设置seed
torch.manual_seed(m_seed)


class Actor(nn.Module):
    def __init__(self, input_num, hidden_num, num_output, layers=2):
        super(Actor, self).__init__()
        self.hidden_dim = hidden_num
        self.n_layers = layers
        self.rnn = nn.GRU(
            input_size=input_num,
            hidden_size=hidden_num,  # rnn hidden unit
            num_layers=self.n_layers,  # number of rnn layer
            batch_first=True,  # input & output will has batch size as 1s dimension. e.g. (batch, time_step, input_size)
        )
        self.action_head = nn.Linear(hidden_num, num_output)

    def forward(self, x):
        batch_size = x.size(0)
        h_0 = self.init_hidden(batch_size)
        r_out, h_state = self.rnn(x.view(len(x), 1, -1), h_0)
        x = r_out[:, -1, :]
        action_prob = F.softmax(self.action_head(x), dim=1)
        return action_prob

    def init_hidden(self, batch_size):
        # This method generates the first hidden state of zeros which we'll use in the forward pass
        hidden = torch.zeros(self.n_layers, batch_size, self.hidden_dim)
        # We'll send the tensor holding the hidden state to the device we specified earlier as well
        return hidden


class Critic(nn.Module):
    def __init__(self, input_num, hidden_num, num_output=1, layers=2):
        super(Critic, self).__init__()
        self.hidden_dim = hidden_num
        self.n_layers = layers
        self.rnn = nn.GRU(
            input_size=input_num,
            hidden_size=hidden_num,  # rnn hidden unit
            num_layers=self.n_layers,  # number of rnn layer
            batch_first=True,  # input & output will has batch size as 1s dimension. e.g. (batch, time_step, input_size)
        )
        self.state_value = nn.Linear(hidden_num, num_output)

    def forward(self, x):
        batch_size = x.size(0)
        h_0 = self.init_hidden(batch_size)
        r_out, h_state = self.rnn(x.view(len(x), 1, -1), h_0)
        x = r_out[:, -1, :]
        value = self.state_value(x)
        return value

    def init_hidden(self, batch_size):
        # This method generates the first hidden state of zeros which we'll use in the forward pass
        hidden = torch.zeros(self.n_layers, batch_size, self.hidden_dim)
        # We'll send the tensor holding the hidden state to the device we specified earlier as well
        return hidden


class PPO:
    def __init__(self, j_env, unit_num=100, memory_size=5, batch_size=32, clip_ep=0.2):
        super(PPO, self).__init__()
        self.env = j_env
        self.memory_size = memory_size
        self.batch_size = batch_size  # update batch size
        self.epsilon = clip_ep

        self.state_dim = self.env.num_state
        self.action_dim = self.env.action_num
        self.case_name = self.env.case_name
        self.gamma = 0.999  # reward discount
        self.A_LR = 1e-3  # learning rate for actor
        self.C_LR = 3e-3  # learning rate for critic
        self.UPDATE_STEPS = 10  # update steps
        self.max_grad_norm = 0.5

        self.actor_net = Actor(self.state_dim, unit_num, self.action_dim)
        self.critic_net = Critic(self.state_dim, unit_num)
        self.actor_optimizer = optimizer.Adam(self.actor_net.parameters(), self.A_LR)
        self.critic_net_optimizer = optimizer.Adam(self.critic_net.parameters(), self.C_LR)
        if not os.path.exists('param'):
            os.makedirs('param/net_param')
        self.alpha = 0.6  # parameters for priority replay
        self.capacity = self.memory_size*self.env.total_num_task
        self.priorities = np.zeros([self.capacity], dtype=np.float32)
        self.training_step = 0
        self.init_size = 1
        self.convergence_episode = 2000

    def select_action(self, state):
        state = torch.from_numpy(state).float().unsqueeze(0)
        with torch.no_grad():
            action_prob = self.actor_net(state)
        c = Categorical(action_prob)
        action = c.sample()
        return action.item(), action_prob[:, action.item()].item()

    def get_value(self, state):
        state = torch.tensor(state, dtype=torch.float)
        with torch.no_grad():
            value = self.critic_net(state)
        return value.item()

    def save_params(self):
        torch.save(self.actor_net.state_dict(), 'param/net_param/' + self.env.case_name + '_actor_net.model')
        torch.save(self.critic_net.state_dict(), 'param/net_param/' + self.env.case_name + '_critic_net.model')

    def load_params(self, model_name):
        self.critic_net.load_state_dict(torch.load('param/net_param/' + model_name + '_critic_net.model'))
        self.actor_net.load_state_dict(torch.load('param/net_param/' + model_name + '_actor_net.model'))

    def learn(self, state, action, d_r, old_prob):
        #  compute the advantage
        d_reward = d_r.view(-1, 1)
        V = self.critic_net(state)
        delta = d_reward - V
        advantage = delta.detach()

        # epoch iteration, PPO core!
        action_prob = self.actor_net(state).gather(1, action)  # new policy
        ratio = (action_prob / old_prob)
        surrogate = ratio * advantage
        clip_loss = torch.clamp(ratio, 1 - self.epsilon, 1 + self.epsilon) * advantage
        action_loss = -torch.min(surrogate, clip_loss).mean()

        # update actor network
        self.actor_optimizer.zero_grad()
        action_loss.backward()
        nn.utils.clip_grad_norm_(self.actor_net.parameters(), self.max_grad_norm)
        self.actor_optimizer.step()

        # update critic network
        value_loss = torch.sum((d_reward-V).pow(2)/d_reward.size(0))
        self.critic_net_optimizer.zero_grad()
        value_loss.backward()
        nn.utils.clip_grad_norm_(self.critic_net.parameters(), self.max_grad_norm)
        self.critic_net_optimizer.step()
        # calculate priorities
        for i in range(len(advantage)):
            if advantage[i] < 0:
                advantage[i] = 1e-5
        prob = advantage ** self.alpha
        return np.array(prob).flatten()

    def update(self, bs, ba, br, bp):
        # get old actor log prob
        old_log_prob = torch.tensor(bp, dtype=torch.float).view(-1, 1)
        state = torch.tensor(np.array(bs), dtype=torch.float)
        action = torch.tensor(ba, dtype=torch.long).view(-1, 1)
        d_reward = torch.tensor(br, dtype=torch.float)

        for i in range(self.UPDATE_STEPS):
            self.training_step += 1
            # # replay all experience
            for index in BatchSampler(SubsetRandomSampler(range(len(ba))), self.batch_size, False):
                self.priorities[index] = self.learn(state[index], action[index], d_reward[index], old_log_prob[index])
            # priority replay
            prob1 = self.priorities / np.sum(self.priorities)
            replay_size = self.init_size + (self.batch_size - self.init_size) * pow(
                self.training_step / self.convergence_episode, 2)
            indices = np.random.choice(len(ba), min(self.batch_size, int(replay_size)), p=prob1)
            self.learn(state[indices], action[indices], d_reward[indices], old_log_prob[indices])

    def train(self, model_name, is_reschedule=False):
        if is_reschedule:
            self.load_params(model_name)
        column = ["episode", "make_span", "reward", "min_make_span"]
        results = pd.DataFrame(columns=column, dtype=float)
        index = 0
        converged = 0
        min_make_span = 1e10
        converged_value = []
        t0 = time.time()
        for i_epoch in range(20):
            if time.time() - t0 >= 360:
                break
            bs, ba, br, bp = [], [], [], []
            for m in range(self.memory_size):  # memory size is the number of complete episode
                buffer_s, buffer_a, buffer_r, buffer_p = [], [], [], []
                state = self.env.reset()
                episode_reward = 0
                while True:
                    action, action_prob = self.select_action(state)
                    next_state, reward, done = self.env.step(action)
                    buffer_s.append(state)
                    buffer_a.append(action)
                    buffer_r.append(reward)
                    buffer_p.append(action_prob)

                    state = next_state
                    episode_reward += reward
                    if done:
                        v_s_ = 0
                        discounted_r = []
                        for r in buffer_r[::-1]:
                            v_s_ = r + self.gamma * v_s_
                            discounted_r.append(v_s_)
                        discounted_r.reverse()

                        bs[len(bs):len(bs)] = buffer_s
                        ba[len(ba):len(ba)] = buffer_a
                        br[len(br):len(br)] = discounted_r
                        bp[len(bp):len(bp)] = buffer_p
                        index = i_epoch * self.memory_size + m
                        if min_make_span > self.env.current_time:
                            min_make_span = self.env.current_time
                        # Episode: make_span: Episode reward: no-op count
                        print('{}    {}    {:.2f}  {}'.format(i_epoch, self.env.current_time,
                                                              episode_reward, min_make_span))
                        results.loc[index] = [i_epoch, self.env.current_time, episode_reward, min_make_span]
                        converged_value.append(self.env.current_time)
                        if len(converged_value) >= 31:
                            converged_value.pop(0)
                        break
            self.update(bs, ba, br, bp)
            converged = index
            if min(converged_value) == max(converged_value) and len(converged_value) >= 30:
                converged = index
                break
        if not os.path.exists('results'):
            os.makedirs('results')
        results.to_csv("results/" + str(self.env.case_name) + "_" + model_name + ".csv")
        if not is_reschedule:
            self.save_params()
        return min(converged_value), converged, time.time() - t0, min_make_span

    def test(self, data_set):
        self.load_params(data_set)
        value = []
        for m in range(3):
            state = self.env.reset()
            while True:
                action, _ = self.select_action(state)
                next_state, reward, done = self.env.step(action)
                state = next_state
                if done:
                    break
            value.append(self.env.current_time)
        return min(value), 0, 0, 0


