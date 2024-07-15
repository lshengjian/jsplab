import argparse
import numpy as np
from typing import List
from src0.data_generator.instance_factory import  generate_instances_from_config,compute_initial_instance_solution
# Config and data handling imports
from src0.utils.file_handler.config_handler import ConfigHandler
from src0.utils.file_handler.data_handler import DataHandler
from src0.agents.train import main
import random
# constants
DEADLINE_HEURISTIC = 'rand'
SEED = 0



if __name__ == '__main__':

    # get config_file from terminal input
    #parse_args = get_parser_args()
    config_file_path ='training/ppo/config_job3_task4_tools0.yaml'

    main(config_file_name=config_file_path)