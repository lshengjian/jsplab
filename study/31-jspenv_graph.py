import numpy as np

from src.envs.jsp_graph import GraphJspEnv
from src.envs.jsp_graph.logger import log


def left_shift_jsp_example() -> None:
    jsp = np.array([
        [
            [0, 1, 2],  # job 0
            [2, 0, 1],  # job 1
            [0, 2, 1]  # job 2
        ],
        [
            [1, 1, 5],  # task durations of job 0
            [5, 3, 3],  # task durations of job 1
            [3, 6, 3]  # task durations of job 2
        ]

    ])
    # _, _, df, _ = or_tools_solver.solve_jsp(jsp_instance=jsp, plot_results=True)

    env = GraphJspEnv(
        jps_instance=jsp,
        perform_left_shift_if_possible=False,
        action_mode='job'
    )
    log.info("without left shift:")
    for s in [0, 1, 0, 1, 2]:
        env.step(s)
    env.render(show=["gantt_console"])


    log.info("with left shift:")
    env = GraphJspEnv(
        jps_instance=jsp,
        perform_left_shift_if_possible=True,
        action_mode='job'
    )
    for s in [0, 1, 0, 1, 2]:
        env.step(s)
    env.render(show=["gantt_console"])


if __name__ == '__main__':
    left_shift_jsp_example()