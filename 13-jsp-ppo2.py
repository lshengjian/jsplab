import gymnasium as gym
import jsplab.envs
import numpy as np
from jsplab import JSP_Data,InstanceJSP
from jsplab.utils import  load_data_list

from pathlib import Path
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

MN='jsp-ppo'
def train():
    dir = Path(__file__).parent
    instances = load_data_list(dir/'data/jsp_demo/study')
    jsp: InstanceJSP = instances[0]
    data=np.array(jsp.to_list2())
    
    envs = make_vec_env("jsp-graph-v1", n_envs=6, seed=0,env_kwargs={
        'jps_instance':data,
        'action_mode':'job',
        'default_visualisations':["gantt_console"],
        'perform_left_shift_if_possible':True
        })
 
    model = PPO("MlpPolicy", envs, verbose=0)
    # Train the agent and display a progress bar
    model.learn(total_timesteps=int(2e5), progress_bar=True)
    # Save the agent
    model.save(MN)
    del model  # delete trained model to demonstrate loading

def play():
    env = gym.make('jsp-graph-v1',action_mode='job',perform_left_shift_if_possible=True, render_mode='human')
    model = PPO.load(MN, env=env)

    # Evaluate the agent
    # NOTE: If you use wrappers with your environment that modify rewards,
    #       this will be reflected here. To evaluate with original rewards,
    #       wrap environment in a "Monitor" wrapper before other wrappers.
    #mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)

    # Enjoy trained agent
    vec_env = model.get_env()
    obs = vec_env.reset()

    for i in range(100):
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, dones, info = vec_env.step(action)
        vec_env.render("human")

def main():
    train()
    play()
    
if __name__ == '__main__':
    main()