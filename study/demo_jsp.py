import JSSEnv
import gymnasium as gym
import numpy as np
if __name__ == '__main__':
    env_config={'instance_path':'JSSEnv/instances/ta01'}
    env = gym.make('jss-v1',env_config=env_config)
    obs,info = env.reset()
    done = False
    cum_reward = 0
    while not done:
        legal_actions = info["action_mask"]

        action = np.random.choice(
            len(legal_actions), 1, p=(legal_actions / legal_actions.sum())
        )[0]
        print(legal_actions,action)
        obs, rewards, done, _,info = env.step(action)
        cum_reward += rewards
    print(f"Cumulative reward: {cum_reward}")
    print(f"solution: {env.solution}")