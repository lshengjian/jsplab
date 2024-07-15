import io

import shutil
import itertools

import networkx as nx
import pandas as pd


from typing import Union, Dict
from .logger import log


class Visualizer:
    """
    this class contains the code for all the different rendering options of a `FjspEnv`,
    but it can be also used as a standalone visualizer.
    """

    COLOR_ESCAPE_SEQUENCE = '\33[0m'

    @staticmethod
    def rgb_color_sequence(r: Union[int, float], g: Union[int, float], b: Union[int, float],
                           *, format_type: str = 'foreground') -> str:
        """
        generates a color-codes, that change the color of text in console outputs.

        rgb values must be numbers between 0 and 255 or 0.0 and 1.0.

        :param r:               red value.
        :param g:               green value
        :param b:               blue value

        :param format_type:     specifies weather the foreground-color or the background-color shall be adjusted.
                                valid options: 'foreground','background'
        :return:                a string that contains the color-codes.
        """
        # type: ignore # noqa: F401
        if format_type == 'foreground':
            f = '\033[38;2;{};{};{}m'.format  # font rgb format
        elif format_type == 'background':
            f = '\033[48;2;{};{};{}m'.format  # font background rgb format
        else:
            raise ValueError(f"format {format_type} is not defined. Use 'foreground' or 'background'.")
        rgb = [r, g, b]

        if isinstance(r, int) and isinstance(g, int) and isinstance(b, int):
            if min(rgb) < 0 and max(rgb) > 255:
                raise ValueError("rgb values must be numbers between 0 and 255 or 0.0 and 1.0")
            return f(r, g, b)
        if isinstance(r, float) and isinstance(g, float) and isinstance(b, float):
            if min(rgb) < 0 and max(rgb) > 1:
                raise ValueError("rgb values must be numbers between 0 and 255 or 0.0 and 1.0")
            return f(*[int(n * 255) for n in [r, g, b]])

    @staticmethod
    def wrap_with_color_codes(s: object, /, r: Union[int, float], g: Union[int, float], b: Union[int, float], **kwargs) \
            -> str:
        """
        stringify an object and wrap it with console color codes. It adds the color control sequence in front and one
        at the end that resolves the color again.

        rgb values must be numbers between 0 and 255 or 0.0 and 1.0.

        :param s: the object to stringify and wrap
        :param r: red value.
        :param g: green value.
        :param b: blue value.
        :param kwargs: additional argument for the 'DisjunctiveGraphJspVisualizer.rgb_color_sequence'-method.
        :return:
        """
        return f"{Visualizer.rgb_color_sequence(r, g, b, **kwargs)}" \
               f"{s}" \
               f"{Visualizer.COLOR_ESCAPE_SEQUENCE}"

    @staticmethod
    def gantt_chart_console(df: pd.DataFrame, colors: Dict) -> None:
        """
        console version of the `gantt_chart_rgb_array`-method. prints a gant chart to the console.
        the parameters need to follow the plotly specification.
        see: https://plotly.com/python/gantt/ or `gantt_chart_rgb_array`

        :param df:      dataframe according to `plotly` specification (https://plotly.com/python/gantt/).

        :param colors:  a dict that maps resources to color values. see example below.
                        Note: make sure that the key match the resources specified in `:param df:`

        :return:        a `plotly` gantt chart as rgb array.

        color example

            import numpy as np

            c_map = plt.cm.get_cmap("jet")  # select the desired cmap
            arr = np.linspace(0, 1, 10)  # create a list with numbers from 0 to 1 with n items
            colors = {resource: c_map(val) for resource, val in enumerate(arr)}
        """
        w, h = shutil.get_terminal_size((80, 20))  # enable emulate output in terminal ...

        if len(df) > 0:
            machines = sorted(df['Resource'].unique())
            jobs = df['Task'].unique()
            jobs.sort()
        else:
            jobs, machines = None, None

        len_prefix = 10
        len_suffix = 15

        x_pixels = w - len_prefix - len_suffix
        x_max = df['Finish'].max() + 1 if len(df) > 0 else x_pixels
        if x_pixels < 0:
            log.warn("terminal window to small")
            return

        x_axis_tick_small = "╤════"
        x_axis_tick_big = "╦════"
        len_tick = len(x_axis_tick_big)
        num_hole_ticks = x_pixels // len_tick
        len_last_tick = x_pixels % len_tick
        x_axis = "".join([
            f"{'':<{len_prefix - 1}}╚",
            *[x_axis_tick_big if i % 5 == 0 else x_axis_tick_small for i in range(num_hole_ticks)],
            "═" * len_last_tick + "╝"
        ])
        x_chart_frame_top = "".join([
            f"{'':<{len_prefix - 1}}╔",
            "═" * x_pixels,
            "╗"
        ])

        x_interval_increment5 = x_max / num_hole_ticks
        x_interval_increment1 = x_max / x_pixels

        x_axis_label = "".join([
            f"{'':<{len_prefix}}",
            *[
                f"{f'{i * x_interval_increment5:.1f}':<5}" if i % 5 == 0 else f"{'':<5}"
                for i in range(num_hole_ticks)
            ]
        ])

        rows = []
        if len(df) > 0:
            for j, m in itertools.zip_longest(jobs, machines):
                matching_tasks = df.loc[df['Task'] == j].iterrows()
                chart_str = [i * x_interval_increment1 for i in range(x_pixels)]
                for _, (_, start, finish, resource) in matching_tasks:
                    chart_str = [
                        f"{Visualizer.rgb_color_sequence(*colors[resource])}█"
                        if not isinstance(v, str) and start <= v <= finish else v for v in chart_str
                    ]
                prefix = f"{f'{j}':<{len_prefix - 1}}║" if j else f"{'':<{len_prefix - 1}}║"
                colored_block = Visualizer.wrap_with_color_codes("█", *colors[m]) if m else None
                suffix = f"{f'║ {m}':<{len_suffix - 1}}" + f"{colored_block}" if m else f"{f'║':<{len_suffix}}"

                chart_str = [" " if not isinstance(v, str) else v for v in chart_str]
                chart_str = "".join(chart_str)
                rows.append(f"{prefix}{chart_str}{Visualizer.COLOR_ESCAPE_SEQUENCE}{suffix}")
        else:
            rows = ["".join([f"{f'':<{len_prefix - 1}}║", " " * x_pixels, "║"])]

        gant_str = "\n".join([
            x_chart_frame_top,
            *rows,
            x_axis,
            x_axis_label
        ])
        print(gant_str)


    def __init__(self, *,
                 dpi=55, width=15, height=10,
                 scheduled_color="#DAF7A6", not_scheduled_color="#FFC300", color_job_edge="tab:gray",
                 node_drawing_kwargs=None,
                 edge_drawing_kwargs=None,
                 critical_path_drawing_kwargs=None):
        """
        :param dpi:                             parameter for `matplotlib.pyplot.figure`
        :param width:                           parameter for `matplotlib.pyplot.figure`
        :param height:                          parameter for `matplotlib.pyplot.figure`

        :param scheduled_color:                 parameter for `nx.draw_networkx_nodes`
        :param not_scheduled_color:             parameter for `nx.draw_networkx_nodes`
        :param color_job_edge:                  parameter for `nx.draw_networkx_edges`

        :param node_drawing_kwargs:             kwargs for `nx.draw_networkx_nodes`
        :param edge_drawing_kwargs:             kwargs for `nx.draw_networkx_nodes`
        :param critical_path_drawing_kwargs:    kwargs for `nx.draw_networkx_edges`
        """
        self.width = width
        self.height = height
        self.dpi = dpi
        self.color_scheduled = scheduled_color
        self.color_not_scheduled = not_scheduled_color
        self.color_job_edge = color_job_edge
        self.node_drawing_kwargs = {
            "node_size": 800,
            "linewidths": 5
        } if node_drawing_kwargs is None else node_drawing_kwargs
        self.edge_drawing_kwargs = {
            "arrowsize": 30
        } if edge_drawing_kwargs is None else edge_drawing_kwargs
        self.critical_path_drawing_kwargs = {
            "edge_color": 'r',
            "width": 20,
            "alpha": 0.1,
        } if critical_path_drawing_kwargs is None else critical_path_drawing_kwargs


    @staticmethod
    def graph_console(G: nx.DiGraph, /, shape: tuple, colors: dict) -> None:
        """
        console version of the `graph_rgb_array`-method. prints a graph that indicates which tasks are scheduled to
        the console.

        :param G:       the `nx.DiGraph` of an `DisjunctiveGraphJssEnv` instance
        :param shape:   size of the jsp
        :param colors:  a dict that maps resources to color values. see example below.
                        Note: make sure that the key match the resources specified in `:param df:`

        :return:        None

        import numpy as np

            c_map = plt.cm.get_cmap("jet")  # select the desired cmap
            arr = np.linspace(0, 1, 10)  # create a list with numbers from 0 to 1 with n items
            colors = {resource: c_map(val) for resource, val in enumerate(arr)}
        """
        w, _ = shutil.get_terminal_size((80, 20))
        n_jobs, n_machines = shape

        len_prefix = 10
        len_suffix = 15

        if w < 2 * n_jobs + len_prefix + len_suffix:
            log.warn("terminal window to small")
            return

        task_id = 0
        machine_strings = [
            f"{m :>{len_suffix - 5}} {Visualizer.wrap_with_color_codes('█', r, g, b)}"
            for m, (r, g, b) in colors.items()
        ]

        for j, m_str in itertools.zip_longest(range(n_jobs), machine_strings):
            row = f"Job {j}" if j is not None else ""
            row = f"{row:<{len_prefix}}"
            for task_in_job in range(n_machines):
                task_id = task_id + 1
                if task_id < len(G.nodes) - 1:
                    node = G.nodes[task_id]
                    node_str = "●" if node["scheduled"] else "◯"
                    r, g, b, *_ = node["color"]
                    node_str = Visualizer.wrap_with_color_codes(node_str, r, g, b)
                    if task_in_job < n_machines - 1:
                        node_str += "-"
                else:
                    node_str = " "
                    if task_in_job < n_machines - 1:
                        node_str += " "
                row += node_str
            print("".join([row, " " * 4, m_str if m_str is not None else ""]))






