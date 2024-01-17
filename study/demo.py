from  epsolver.utils.instance import load_data_from_files
from epsolver import FJSP_DATA
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from fjsp.visualizer import Visualizer
import numpy as np
import pandas as pd
def main():
    data:FJSP_DATA=load_data_from_files('data/Demo')[0]
    print(data.num_tasks)
    print(data.op_times)

    G = nx.DiGraph()

    # Add nodes for source and sink
    G.add_node('source', pos=(0, 0.5),job=-1)
    G.add_node('sink', pos=(10, 0.5),job=-1)

    start=0
    for jid,n_tasks in enumerate(data.num_tasks):
        for k in range(n_tasks):
            flag=f'J{jid+1}_{k+1}'
            op_times=data.op_times[k]
            idxs=np.where(op_times>0)[0]
            mid=np.random.choice(idxs,1)[0]
            #print(mid)
            G.add_node(flag, pos=(k+1, jid),
                       job=jid,machine=mid,start_time=start,finish_time=start+op_times[mid]) 
            start=start+op_times[mid]
            if k==0:
                G.add_edge('source', flag)
            if k==n_tasks-1:
                G.add_edge(flag, 'sink')




# Add conjunctive edges (precedence constraints within the same job)
# G.add_edge('J1_1', 'J1_2', conjunctive=True)
# G.add_edge('J1_1', 'J2_1', disjunctive=True, machine='M1')


# # For visualization, draw conjunctive edges in black and disjunctive edges in red
# edge_colors = ['red' if 'conjunctive' in G[u][v] else 'black' for u, v in G.edges()]

# # Draw graph
    #pos = nx.get_node_attributes(G, 'pos')
    #nx.draw(G, pos, with_labels=True, node_size=80) #edge_color=edge_colors,
    c_map = matplotlib.colormaps["rainbow"]
    arr = np.linspace(0, 1, data.op_times.shape[1], dtype=float)
    machine_colors = {m_id: c_map(val)  for m_id, val in enumerate(arr)}
    colors = {f"M_{m_id}": (r, g, b) for m_id, (r, g, b, a) in machine_colors.items()}
    print(colors)
    df=pd.DataFrame([
            {
                'Task': f'Job {data["job"]}',
                'Start': data["start_time"],
                'Finish': data["finish_time"],
                'Resource': f'M_{data["machine"]}'
            }
            for task_id, data in G.nodes(data=True)
            if data["job"] != -1 and data["finish_time"] is not None
        ])

    Visualizer.gantt_chart_console(df,colors)
    #nx.draw_networkx_edges(G, pos)


if __name__ == '__main__':
    main()
    #plt.show()

    