from jsplab.utils import draw_timeway
from jsplab.utils import TextHelper

if __name__ == "__main__":
    #T2~T3是加工槽位，加工时间均为20s,取出及放下时间均为2s
    #天车1初始位置在T1,天车2初始位置在T5
    tanks=TextHelper.get_numpy_data('data/epsp/tanks.csv').astype(int)
    #print(tanks[:,0:5])
    times=TextHelper.get_numpy_data('data/epsp/free_move_times.csv').astype(int)
    num_hoists = 3  # Hoist数量
    num_tanks = tanks.shape[-1]  # 处理槽数量
    min_processing_time = tanks[2,:]  # 每个处理槽的最小加工时间
    max_processing_time = tanks[3,:]   # 
    offsets=list(map(int,tanks[0,:]))
    print(list(offsets))
    seq=list(tanks[1,:])+[0]
    hts = [0] * num_tanks  # 执行搬运作业所需时间
    ss=[]
    for i in range(num_tanks):
        s1=seq[i]
        s2=seq[i+1]
        ss.append(offsets[s1])
        hts[i]=times[s1,s2]+20
    print(ss)
    tanks = [f'T{i}' for i in range(num_tanks)]
    tank_positions = {tank: offsets[i] for i, tank in enumerate(tanks)}
    hoist_moves = {
            'H1': [('T0', 'T4', 0, 31, 1)],
            'H2': [('T4', 'T5', 9, 32, 1),('T5', 'T7', 136, 158, 1),('T7', 'T6', 80, 102, 1)],
            'H3': [('T6', 'T8', 192, 217, 1),('T8', 'T9', 31, 54, 1)]
        }
    for ms in hoist_moves.values():
        for m in ms:
            t1,t2=int(m[0][1:]),int(m[1][1:])
            print(m[3],m[2]+times[t1,t2]+20)
            #assert m[3]==m[2]+times[offsets[t1],offsets[t2]]+20+3

    draw_timeway('demo1(T=216)',tank_positions,hoist_moves)

