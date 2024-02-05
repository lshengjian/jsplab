import warnings

from typing import Tuple, Any
from .env_tetris_scheduling import Env
from .env_tetris_scheduling_indirect_action import IndirectActionEnv

# Constants
DEFAULT_ENVIRONMENT_NAME: str = 'env_tetris_scheduling'
ENVIRONMENT_MAPPER_DICT: dict = {
    'env_tetris_scheduling': {
        'class': Env,
        'compatible_algorithms': ['ppo_masked']
    },
    'env_tetris_scheduling_indirect_action': {
        'class': IndirectActionEnv,
        'compatible_algorithms': ['dqn', 'ppo']
    }
}


class EnvironmentLoader:
    """
    Loads the right environment as named in the passed config file.
    Also checks if the environment is compatible with the chosen algorithm.
    """
    @classmethod
    def load(cls, config: dict, check_env_agent_compatibility: bool = False, register_gym_env: bool = False, **kwargs) -> Tuple[Any, str]:
        """loading function"""

        env_name = config.get("environment", DEFAULT_ENVIRONMENT_NAME)

        if check_env_agent_compatibility:
            cls.check_environment_agent_compatibility(config, env_name=env_name)

        # Create environment.
        env = ENVIRONMENT_MAPPER_DICT[env_name]['class'](config, **kwargs)

        return env, env_name

    @classmethod
    def check_environment_agent_compatibility(cls, config: dict, env_name: str = None, algo_name: str = None):
        """
        Check if environment and algorithm are compatible. E.g., some environments may depend on action masking.
        """
        # Get requested environment and algorithm names
        _env_name = env_name if env_name else config.get('environment')
        _algo_name = algo_name if algo_name else config.get('algorithm')

        # Warn if environment and algorithm not compatible
        if _algo_name not in ENVIRONMENT_MAPPER_DICT[_env_name]['compatible_algorithms']:
            warnings.warn(f'\n Environment {_env_name} not compatible with {_algo_name}, but was set in config.\n'
                          f' This may lead to unexpected errors. Please check and update your config or '
                          f'ENVIRONMENT_MAPPER_DICT constant in environment_loader.py')
