import gymnasium as gym
import sb3_contrib
import numpy as np
import stable_baselines3 as sb3


from jsplab.envs.jsp_graph import log,GraphJspEnv

from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from jsplab import InstanceJSP
from jsplab.instances import  load_data_list
from pathlib import Path
def mask_fn(env: gym.Env) -> np.ndarray:
    return env.valid_action_mask()

def train():
    dir = Path(__file__).parent
    instances = load_data_list(dir/'data/jsp_demo/study')
    jsp: InstanceJSP = instances[0]
    data=np.array(jsp.to_list2())


    env = GraphJspEnv(
        jps_instance=data,
        default_visualisations=["gantt_console"],
        perform_left_shift_if_possible=True,
        normalize_observation_space=True,
        flat_observation_space=True,
        action_mode='job',  # alternative 'task'
    )
    env = sb3.common.monitor.Monitor(env)

    env = ActionMasker(env, mask_fn)

    model = sb3_contrib.MaskablePPO(MaskableActorCriticPolicy, env, verbose=0)

    # Train the agent
    log.info("training the model")
    model.learn(total_timesteps=20_000)
    model.save('jsp-3x3')

if __name__ == '__main__':
    train()