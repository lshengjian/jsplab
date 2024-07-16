
from src.core.parsers import  IParse,ExcelFileParser
from src.agents.heuristic import HeuristicSelectionAgent
from src.envs.epsp_env import PlateJobShopEnv
from typing import Union,List,Tuple



def get_action(env,  heuristic_id: str, heuristic_agent: HeuristicSelectionAgent) -> Tuple[int, str]:
    """
    This function determines the next action according to the input model or heuristic

    :param env: Environment object
    :param model: Model object. E.g. PPO object
    :param heuristic_id: Heuristic identifier. Can be None
    :param heuristic_agent: HeuristicSelectionAgent object. Can be None

    :return: ID of the selected action

    """
    obs = env.state_obs
    mask = env.get_action_mask()

    action_mode = 'heuristic'
    tasks = env.tasks
    task_mask = mask
    selected_action = heuristic_agent(tasks, task_mask, heuristic_id)
    return selected_action, action_mode
def run_episode(env,  heuristic_id: Union[str, None]) -> None:
    """
    This function executes one testing episode

    :param env: Environment object
    :param heuristic_id: Heuristic identifier. Can be None
    :param handler: EvaluationHandler object

    :return: None

    """
    done = False
    total_reward = 0
    agent=HeuristicSelectionAgent()

    # run agent on environment and collect rewards until done
    steps = 0
    while not done:
        steps += 1
        action, action_mode = get_action(env,  heuristic_id, agent)

        b = env.step(action, action_mode=action_mode)
        total_reward += b[1]
        done = b[2]

    # store episode in object
    mean_reward = total_reward / steps
    print(mean_reward)

if __name__ == '__main__':
    parser:IParse=ExcelFileParser()
    info=parser.parse('fjsp/demo/3x3-same.xlsx')
    # steps,actions=solve_fjsp(info)
    # print("or-tools:",steps)
    # print(actions)
    # instance_list=[info.tasks]
    env=PlateJobShopEnv({},[info.tasks]*1)


    TEST_HEURISTICS = ['rand','MTR','SPT', 'LTR']#'MTR' is best
    for t in TEST_HEURISTICS:
        env.reset()
        run_episode(env,t)
        print(t,env.get_makespan())
        #print(env.action_history)