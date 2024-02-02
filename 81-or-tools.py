import argparse
import numpy as np
from typing import List
from src.data_generator.instance_factory import  generate_instances_from_config,compute_initial_instance_solution
# Config and data handling imports
from src.utils.file_handler.config_handler import ConfigHandler
from src.utils.file_handler.data_handler import DataHandler
from src.agents.solver import OrToolSolver
from src.data_generator.task import Task
from src.data_generator.sp_factory import SPFactory
import random
# constants
DEADLINE_HEURISTIC = 'rand'
SEED = 0
def main(config_file_name=None, external_config=None):
    # get config
    current_config: dict = ConfigHandler.get_config(config_file_name, external_config)

    # set seeds
    seed = current_config.get('seed', SEED)
    np.random.seed(seed)
    random.seed(seed)

    # Generate instances
    generated_instances: List[List[Task]] = generate_instances_from_config(current_config)

    # Create instance list
    instance_list: List[List[Task]] = compute_initial_instance_solution(generated_instances, current_config)

    # Assign deadlines in-place
    SPFactory.set_deadlines_to_max_deadline_per_job(instance_list, current_config.get('num_jobs', None))

    # compute individual hash for each instance
    SPFactory.compute_and_set_hashes(instance_list)

    # Write resulting instance data to file
    #if current_config.get('write_to_file', True):
    #DataHandler.save_instances_data_file(current_config, instance_list)

    or_tool_solver = OrToolSolver()
    solved_data = []

    for sample_instance in instance_list:
        # find solution
        assigned_jobs, objective_value = or_tool_solver.optimize(sample_instance, objective='makespan')
        print(objective_value)



if __name__ == '__main__':

    # get config_file from terminal input
    #parse_args = get_parser_args()
    #config_file_path ='data_generation/jssp/config_job2_task3_tools0.yaml'
    config_file_path ='data_generation/jssp/config_job3_task4_tools0.yaml'
    main(config_file_name=config_file_path)