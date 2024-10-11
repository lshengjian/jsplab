from jsplab.utils import draw_timeway


if __name__ == "__main__":
    #T2~T3是加工槽位，加工时间均为20s,取出及放下时间均为2s
    #天车1初始位置在T1,天车2初始位置在T5
    tanks = ['T1', 'T2', 'T3', 'T4', 'T5']
    tank_positions = {tank: i+1 for i, tank in enumerate(tanks)}
    hoist_moves = {
            'H1': [('T1', 'T2', 0, 5, 1),('T2', 'T1', 5, 1, 0),('T1', 'T1', 6, 32-6, 0)],
            'H2': [('T5', 'T5', 0, 22, 0),('T5', 'T2', 22, 3, 0),('T2', 'T5', 25, 7, 1)]
        }
    draw_timeway('demo1(T=32x2)',tank_positions,hoist_moves)

    hoist_moves = {
            'H1': [('T1', 'T2', 0, 5, 1), ('T2', 'T1', 5, 1, 0),('T1', 'T3', 6, 6, 1),('T3', 'T1', 12, 2, 0),('T1', 'T1', 14, 26, 0)],
            'H2': [('T5', 'T5', 0, 22, 0),('T5', 'T2', 22, 3, 0),('T2', 'T5', 25, 7, 1),('T5', 'T3', 32, 2, 0), ('T3', 'T5', 34, 6, 1)]
        }
    draw_timeway('demo2(T=40)',tank_positions,hoist_moves)