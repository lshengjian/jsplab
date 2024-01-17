import gymnasium as gym
import gym_examples
from stable_baselines3 import DQN,PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.envs import SimpleMultiObsEnv
MN='grid-ppo'
def train():
    #env = gym.make('gym_examples/GridWorld-v0', size=3)
    envs = make_vec_env("gym_examples/GridWorld-v0", n_envs=6, seed=0,env_kwargs={'size':3})
    '''
    envs = gym.vector.AsyncVectorEnv(
        [
            lambda: gym.make(
                "LunarLander-v2",
                gravity=np.clip(
                    np.random.normal(loc=-10.0, scale=1.0), a_min=-11.99, a_max=-0.01
                ),
                enable_wind=np.random.choice([True, False]),
                wind_power=np.clip(
                    np.random.normal(loc=15.0, scale=1.0), a_min=0.01, a_max=19.99
                ),
                turbulence_power=np.clip(
                    np.random.normal(loc=1.5, scale=0.5), a_min=0.01, a_max=1.99
                ),
                max_episode_steps=600,
            )
            for i in range(3)
        ]
    )
    '''

    model = PPO("MultiInputPolicy", envs, verbose=0)
    # Train the agent and display a progress bar
    model.learn(total_timesteps=int(2e5), progress_bar=True)
    # Save the agent
    model.save(MN)
    del model  # delete trained model to demonstrate loading

def play():
    env = gym.make('gym_examples/GridWorld-v0', size=3,render_mode='human')
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
    #train()
    play()
    
if __name__ == '__main__':
    main()